:: This script pushes the current branch to the remote repository and sets up tracking.
:: If the branch does not exist on the remote repository, it is created and tracking is set up.
:: If the branch already exists on the remote repository, it is pushed and tracking is set up.
:: If the push fails, the script exits with an error code.
:: Author: John Firnschild
:: Date: 2023-10-03
:: Version: 1.0.3
:: Have a nice day!

:: Set the remote repository
set "remote=origin"

:: Get the current branch name
for /f "delims=" %%i in ('git rev-parse --abbrev-ref HEAD') do set "branch=%%i"

:: Check if the branch exists on the remote repository
git ls-remote --exit-code %remote% refs/heads/%branch%

if %errorlevel% neq 0 (
    echo Branch "%branch%" does not exist on remote "%remote%".
)

:: Push the current branch to the remote repository and set up tracking
git push -u %remote% %branch%

:: Check the exit code of the git push command
if %errorlevel% equ 0 (
    echo Successfully pushed branch "%branch%" to "%remote%" and set up tracking.
) else (
    echo Failed to push branch "%branch%" to "%remote%".
    exit /b 1
)