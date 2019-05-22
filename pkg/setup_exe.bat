cd .
python setup.py build
xcopy /E /I "path\to\R-3.3.2" ".\build\exe.win32-3.4\R-3.3.2\"
pause