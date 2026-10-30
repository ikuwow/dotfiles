"""Tests for bin/pr-monitor, on the standard library alone.

Run with: python3 -m unittest discover -s claude-plugins/pr-watch/tests
"""

import contextlib
import http.server
import importlib.machinery
import importlib.util
import io
import json
import os
import pathlib
import subprocess
import sys
import threading
import unittest
import unittest.mock

SCRIPT = pathlib.Path(__file__).resolve().parent.parent / "bin" / "pr-monitor"

# The script has no .py suffix, so a plain import cannot find it, and a bytecode
# cache would land in bin/, which Claude Code puts on the Bash tool's PATH.
sys.dont_write_bytecode = True
loader = importlib.machinery.SourceFileLoader("pr_monitor", str(SCRIPT))
spec = importlib.util.spec_from_loader("pr_monitor", loader)
pr_monitor = importlib.util.module_from_spec(spec)
loader.exec_module(pr_monitor)


def rollup_of(*contexts):
    return {"commits": {"nodes": [{"commit": {"statusCheckRollup": {"contexts": {"nodes": list(contexts)}}}}]}}


class LineTest(unittest.TestCase):
    BOT = {"__typename": "Bot", "login": "devin"}
    TEAM = {"__typename": "Team", "combinedSlug": "org/team"}

    def test_who(self):
        self.assertEqual(pr_monitor.who(self.BOT), "[BOT] devin")
        self.assertEqual(pr_monitor.who({"__typename": "User", "login": "ikuwow"}), "[USER] ikuwow")
        self.assertEqual(pr_monitor.who(None), "[USER] ?")

    def test_reviewer_label(self):
        self.assertEqual(pr_monitor.reviewer_label(self.TEAM), "[TEAM] org/team")
        self.assertEqual(pr_monitor.reviewer_label({"__typename": "User", "login": "ikuwow"}), "[USER] ikuwow")
        self.assertEqual(pr_monitor.reviewer_label(None), "[?] ?")

    def test_timeline_line(self):
        review = {"__typename": "PullRequestReview", "author": self.BOT}
        actor = {"login": "ikuwow"}
        cases = [
            ({"__typename": "IssueComment", "author": self.BOT}, "NEW_TOP_COMMENT: [BOT] devin"),
            ({**review, "state": "COMMENTED", "body": "Looks off"}, "NEW_REVIEW: [BOT] devin COMMENTED"),
            ({**review, "state": "PENDING", "body": "Draft"}, None),
            ({**review, "state": "APPROVED", "body": ""}, None),
            (
                {"__typename": "ReviewRequestedEvent", "requestedReviewer": self.TEAM, "actor": actor},
                "REVIEW_REQUESTED: [TEAM] org/team by ikuwow",
            ),
            (
                {"__typename": "ReviewRequestRemovedEvent", "requestedReviewer": self.TEAM, "actor": None},
                "REVIEW_REQUEST_REMOVED: [TEAM] org/team by ?",
            ),
            ({"__typename": "ReadyForReviewEvent"}, "READY_FOR_REVIEW"),
            ({"__typename": "ConvertToDraftEvent"}, "CONVERT_TO_DRAFT"),
            ({"__typename": "ReviewDismissedEvent"}, "REVIEW_DISMISSED"),
            ({"__typename": "MergedEvent"}, "STATE: MERGED"),
            ({"__typename": "ClosedEvent"}, "STATE: CLOSED"),
            ({"__typename": "ReopenedEvent"}, "STATE: OPEN"),
            ({"__typename": "SomeNewEvent"}, "SomeNewEvent"),
        ]
        for item, line in cases:
            with self.subTest(item=item):
                self.assertEqual(pr_monitor.timeline_line(item), line)

    def test_timeline_items_skip_null_nodes_and_lines(self):
        merged = {"__typename": "MergedEvent", "id": "M1"}
        pending = {"__typename": "PullRequestReview", "id": "R1", "state": "PENDING", "body": "Draft"}
        self.assertEqual(pr_monitor.timeline_items({"nodes": [None, pending, merged]}), [("M1", "STATE: MERGED")])

    def test_review_seen_pending_prints_when_submitted(self):
        pending = {"__typename": "PullRequestReview", "id": "R1", "state": "PENDING", "body": "Draft"}
        seen = set()
        self.assertEqual(pr_monitor.new_lines(pr_monitor.timeline_items({"nodes": [pending]}), seen, False), [])
        submitted = {**pending, "state": "COMMENTED"}
        self.assertEqual(
            pr_monitor.new_lines(pr_monitor.timeline_items({"nodes": [submitted]}), seen, False),
            ["NEW_REVIEW: [USER] ? COMMENTED"],
        )

    def test_thread_comment_items(self):
        comment = {"id": "C1", "author": self.BOT, "path": "a.py", "line": 3}
        current = {"isResolved": False, "isOutdated": False, "comments": {"nodes": [comment]}}
        self.assertEqual(pr_monitor.thread_comment_items({"nodes": [current]}), [("C1", "NEW_COMMENT: [BOT] devin a.py:3")])
        hidden = [{**current, "isResolved": True}, {**current, "isOutdated": True}]
        self.assertEqual(pr_monitor.thread_comment_items({"nodes": hidden}), [])
        file_level = {"id": "C2", "author": None, "path": "a.py", "line": None}
        self.assertEqual(
            pr_monitor.thread_comment_items({"nodes": [{**current, "comments": {"nodes": [file_level]}}]}),
            [("C2", "NEW_COMMENT: [USER] ? a.py:?")],
        )

    def test_new_lines_seed_then_report_each_id_once(self):
        seen = set()
        self.assertEqual(pr_monitor.new_lines([("a", "A")], seen, True), [])
        self.assertEqual(pr_monitor.new_lines([("a", "A"), ("b", "B")], seen, False), ["B"])
        self.assertEqual(pr_monitor.new_lines([("a", "A"), ("b", "B")], seen, False), [])

    def test_rollup_checks(self):
        cases = [
            (
                rollup_of(
                    {"name": "lint", "status": "COMPLETED", "conclusion": "FAILURE"},
                    {"context": "ci/x", "state": "ERROR"},
                    {"name": "test", "status": "IN_PROGRESS", "conclusion": None},
                    {"name": "odd", "status": "COMPLETED", "conclusion": None},
                ),
                [("lint", "FAILURE"), ("ci/x", "ERROR"), ("test", "IN_PROGRESS"), ("odd", "")],
            ),
            ({"commits": {"nodes": [{"commit": {"statusCheckRollup": None}}]}}, []),
            ({"commits": {"nodes": []}}, []),
            ({}, None),
            ({"commits": {"nodes": [{"commit": {"statusCheckRollup": {"contexts": None}}}]}}, None),
        ]
        for pr, checks in cases:
            with self.subTest(pr=pr):
                self.assertEqual(pr_monitor.rollup_checks(pr), checks)


def body(**fields):
    return {"data": {"repository": {"pullRequest": fields}}}


def poll(state="OPEN", sha="aaaaaaa", decision=None, checks=(), comments=(), items=()):
    """Return the answers to one poll's three queries, in the order the script asks."""
    nodes = [{"name": name, "status": "COMPLETED", "conclusion": value} for name, value in checks]
    thread = {
        "isResolved": False,
        "isOutdated": False,
        "comments": {"nodes": [{"id": c, "path": "a", "line": 1} for c in comments]},
    }
    return (
        body(state=state, headRefOid=sha, reviewDecision=decision, **rollup_of(*nodes)),
        body(reviewThreads={"nodes": [thread]}),
        body(timelineItems={"nodes": [{"__typename": kind, "id": kind} for kind in items]}),
    )


class StubClient:
    """Answer queries in order, so a loop that fails to end raises StopIteration."""

    def __init__(self, *polls):
        self.answers = iter(answer for answers in polls for answer in answers)
        self.token = "held"

    def query(self, _query):
        return next(self.answers)


def watch_lines(client):
    out = io.StringIO()
    with contextlib.redirect_stdout(out):
        pr_monitor.watch(client, 0, None)
    return out.getvalue().splitlines()


class WatchTest(unittest.TestCase):
    RED = [("lint", "FAILURE")]

    def test_state_at_the_start_stays_silent_except_a_red_check(self):
        lines = watch_lines(
            StubClient(
                poll(decision="APPROVED", checks=self.RED, comments=["C1"], items=["IssueComment"]),
                poll(state="MERGED", decision="APPROVED", checks=self.RED, comments=["C1"], items=["IssueComment"]),
            )
        )
        self.assertEqual(lines, ["CHECK: lint (FAILURE) @aaaaaaa", "WATCHING", "STATE: MERGED"])

    def test_check_repeats_only_on_a_new_head_or_a_rerun(self):
        lines = watch_lines(
            StubClient(
                poll(checks=self.RED),
                poll(checks=self.RED),
                poll(sha="bbbbbbb", checks=self.RED),
                poll(sha="bbbbbbb", checks=[("lint", "IN_PROGRESS")]),
                poll(sha="bbbbbbb", checks=self.RED),
                poll(state="MERGED", sha="bbbbbbb", checks=self.RED),
            )
        )
        self.assertEqual(
            lines,
            [
                "CHECK: lint (FAILURE) @aaaaaaa",
                "WATCHING",
                "CHECK: lint (FAILURE) @bbbbbbb",
                "CHECK: lint (FAILURE) @bbbbbbb",
                "STATE: MERGED",
            ],
        )

    def test_reapproval_after_a_dismissal_reports(self):
        lines = watch_lines(
            StubClient(
                poll(decision="APPROVED"),
                poll(),
                poll(decision="APPROVED"),
                poll(state="MERGED", decision="APPROVED"),
            )
        )
        self.assertEqual(lines, ["WATCHING", "REVIEW: APPROVED", "STATE: MERGED"])

    def test_new_items_report_once(self):
        lines = watch_lines(
            StubClient(
                poll(comments=["C1"], items=["IssueComment"]),
                poll(comments=["C1", "C2"], items=["IssueComment", "ReadyForReviewEvent"]),
                poll(comments=["C1", "C2"], items=["IssueComment", "ReadyForReviewEvent"]),
                poll(state="MERGED"),
            )
        )
        self.assertEqual(lines, ["WATCHING", "NEW_COMMENT: [USER] ? a:1", "READY_FOR_REVIEW", "STATE: MERGED"])

    def test_pr_ended_before_the_watch_prints_its_end_once(self):
        self.assertEqual(watch_lines(StubClient(poll(state="MERGED", items=["MergedEvent"]))), ["STATE: MERGED"])

    def test_merge_prints_both_timeline_lines_once(self):
        lines = watch_lines(StubClient(poll(), poll(state="MERGED", items=["MergedEvent", "ClosedEvent"])))
        self.assertEqual(lines, ["WATCHING", "STATE: MERGED", "STATE: CLOSED"])

    def test_close_and_reopen_within_one_interval_keep_watching(self):
        lines = watch_lines(
            StubClient(poll(), poll(state="CLOSED", items=["ClosedEvent", "ReopenedEvent"]), poll(state="MERGED"))
        )
        self.assertEqual(lines, ["WATCHING", "STATE: CLOSED", "STATE: OPEN", "STATE: MERGED"])

    def test_outage_prints_once_and_a_failed_source_seeds_on_recovery(self):
        pr, threads, _ = poll()
        lines = watch_lines(
            StubClient(
                (None,),
                (None,),
                (pr, threads, None),
                (pr, threads, None),
                poll(items=["IssueComment"]),
                poll(state="MERGED"),
            )
        )
        self.assertEqual(
            lines,
            ["POLL_ERROR: graphql (pull request)", "POLL_ERROR: graphql (timeline)", "WATCHING", "STATE: MERGED"],
        )

    def test_unknown_rollup_shape_reports_once_and_the_watch_goes_on(self):
        pr = body(state="OPEN", headRefOid="aaaaaaa", commits="malformed")
        _, threads, timeline = poll()
        lines = watch_lines(StubClient((pr, threads, timeline), (pr, threads, timeline), poll(state="MERGED")))
        self.assertEqual(lines, ["POLL_ERROR: graphql (checks)", "WATCHING", "STATE: MERGED"])

    def test_field_errors_fail_the_pull_request_source(self):
        pr = {**poll()[0], "errors": [{"message": "forbidden"}]}
        lines = watch_lines(StubClient((pr,), poll(state="MERGED")))
        self.assertEqual(lines, ["POLL_ERROR: graphql (pull request)", "STATE: MERGED"])

    def test_failed_pull_request_query_drops_the_token(self):
        client = StubClient((None,), poll(state="MERGED"))
        tokens = []
        original = client.query

        def query(query_text):
            tokens.append(client.token)
            return original(query_text)

        client.query = query
        watch_lines(client)
        self.assertEqual(tokens[:2], ["held", None])

    def test_gone_parent_ends_the_watch_before_any_query(self):
        finished = subprocess.Popen([sys.executable, "-c", ""])
        finished.wait()
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            pr_monitor.watch(StubClient(), 0, finished.pid)
        self.assertEqual(out.getvalue(), "")


class ClientTest(unittest.TestCase):
    """Run the client against a local server, with `gh` stubbed out of the token read."""

    def setUp(self):
        test = self
        self.requests = []
        self.respond = lambda handler: handler.send_json(200, {"data": {"ok": True}})

        class Handler(http.server.BaseHTTPRequestHandler):
            def log_message(self, *_args):
                pass

            def send_json(self, status, payload, headers=()):
                self.send_response(status)
                for name, value in headers:
                    self.send_header(name, value)
                self.end_headers()
                self.wfile.write(json.dumps(payload).encode())

            def handle_request(self):
                self.rfile.read(int(self.headers.get("Content-Length", 0)))
                test.requests.append((self.path, self.headers.get("Authorization")))
                test.respond(self)

            do_POST = handle_request
            do_GET = handle_request

        server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        threading.Thread(target=server.serve_forever, daemon=True).start()
        self.addCleanup(server.server_close)
        self.addCleanup(server.shutdown)
        endpoint = f"http://127.0.0.1:{server.server_address[1]}/graphql"
        patcher = unittest.mock.patch.object(pr_monitor, "ENDPOINT", endpoint)
        patcher.start()
        self.addCleanup(patcher.stop)

    def query(self, *tokens):
        with unittest.mock.patch.object(pr_monitor, "read_token", side_effect=list(tokens) + [None]):
            return pr_monitor.Client("o", "r", 1).query("query")

    def test_success_sends_the_token(self):
        self.assertEqual(self.query("t"), {"data": {"ok": True}})
        self.assertEqual(self.requests, [("/graphql", "bearer t")])

    def test_401_retries_once_with_a_new_token(self):
        self.respond = lambda handler: (
            handler.send_json(401, {})
            if handler.headers.get("Authorization") == "bearer old"
            else handler.send_json(200, {"data": {"ok": True}})
        )
        self.assertEqual(self.query("old", "new"), {"data": {"ok": True}})
        self.assertEqual([auth for _, auth in self.requests], ["bearer old", "bearer new"])

    def test_second_401_fails_after_two_requests(self):
        self.respond = lambda handler: handler.send_json(401, {})
        self.assertIsNone(self.query("a", "b", "c"))
        self.assertEqual(len(self.requests), 2)

    def test_no_token_fails_without_a_request(self):
        self.assertIsNone(self.query(None))
        self.assertEqual(self.requests, [])

    def test_redirect_fails_and_is_not_followed(self):
        self.respond = lambda handler: handler.send_json(302, {}, [("Location", "/target")])
        self.assertIsNone(self.query("secret"))
        self.assertEqual([path for path, _ in self.requests], ["/graphql"])

    def test_server_error_fails(self):
        self.respond = lambda handler: handler.send_json(500, {})
        self.assertIsNone(self.query("t"))

    def test_body_that_is_not_json_fails(self):
        def respond(handler):
            handler.send_response(200)
            handler.end_headers()
            handler.wfile.write(b"<html>")

        self.respond = respond
        self.assertIsNone(self.query("t"))


class ReadTokenTest(unittest.TestCase):
    def read_with(self, *command):
        with unittest.mock.patch.object(pr_monitor, "TOKEN_COMMAND", list(command)):
            return pr_monitor.read_token()

    def test_output_is_stripped(self):
        self.assertEqual(self.read_with(sys.executable, "-c", "print('  tok  ')"), "tok")

    def test_failing_missing_or_silent_gh_gives_no_token(self):
        self.assertIsNone(self.read_with(sys.executable, "-c", "raise SystemExit(1)"))
        self.assertIsNone(self.read_with("/nonexistent/gh"))
        self.assertIsNone(self.read_with(sys.executable, "-c", ""))


class MainTest(unittest.TestCase):
    def test_bad_usage_exits_nonzero_before_watching(self):
        cases = [
            ([], {"GH_REPO": "o/r"}, 1),
            (["1", "2", "3"], {"GH_REPO": "o/r"}, 1),
            (["--help"], {"GH_REPO": "o/r"}, 2),
            (["1\n"], {"GH_REPO": "o/r"}, 2),
            (["1", "0"], {"GH_REPO": "o/r"}, 2),
            (["1"], {}, 2),
            (["1"], {"GH_REPO": "github.com/o/r"}, 2),
        ]
        for args, env, status in cases:
            with self.subTest(args=args, env=env):
                with unittest.mock.patch.dict(os.environ, env, clear=True):
                    with contextlib.redirect_stderr(io.StringIO()):
                        self.assertEqual(pr_monitor.main(["pr-monitor"] + args), status)


class ProcessTest(unittest.TestCase):
    def test_line_reaches_a_pipe_at_once_and_sigterm_ends_quietly(self):
        # An empty PATH leaves no `gh`, so the first query fails with no network.
        process = subprocess.Popen(
            [sys.executable, "-B", str(SCRIPT), "1", "60"],
            env={"PATH": "", "GH_REPO": "o/r"},
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        self.addCleanup(process.stderr.close)
        self.addCleanup(process.stdout.close)
        self.assertEqual(process.stdout.readline(), "POLL_ERROR: graphql (pull request)\n")
        self.assertIsNone(process.poll())
        process.terminate()
        process.wait(timeout=10)
        self.assertEqual(process.stderr.read(), "")


if __name__ == "__main__":
    unittest.main()
