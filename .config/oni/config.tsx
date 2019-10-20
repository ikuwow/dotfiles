import * as React from "react"
import * as Oni from "oni-api"

export const activate = (oni: Oni.Plugin.Api) => {
    console.log("config activated")

    // Input
    //
    // Add input bindings here:
    //
    oni.input.bind("<c-enter>", () => console.log("Control+Enter was pressed"))

    oni.input.unbind("<s-c-b>");
    oni.input.bind("<s-c-q>", "sidebar.toggle");

    //
    // Or remove the default bindings here by uncommenting the below line:
    //
    // oni.input.unbind("<c-p>")

}

export const deactivate = (oni: Oni.Plugin.Api) => {
    console.log("config deactivated")
}

export const configuration = {
    //add custom config here, such as

    "ui.colorscheme": "desert",

    //"oni.useDefaultConfig": true,
    //"oni.bookmarks": ["~/Documents"],
    //"oni.loadInitVim": false,
    "sidebar.enabled": false,

    // UI customizations
    "ui.animations.enabled": true,
    "ui.fontSmoothing": "auto",
    "editor.fontFamily": "Osaka-Mono",
    "editor.fontSize": "14px",
}
