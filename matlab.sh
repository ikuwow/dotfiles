sudo sed -i '' 's/>10.10</>10.90</' /System/Library/CoreServices/SystemVersion.plist
open -a MATLAB_R2013a_Student
read -p "Press any key when MATLAB started..."
sudo sed -i '' 's/>10.90</>10.10</' /System/Library/CoreServices/SystemVersion.plist
