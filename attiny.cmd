@echo off
set ATMEL_HOME=C:\Program Files (x86)\Atmel\Studio\7.0
set PATH=^
%ATMEL_HOME%;^
%ATMEL_HOME%\atbackend;^
%ATMEL_HOME%\shellUtils;^
%ATMEL_HOME%\atpackmanager;^
%ATMEL_HOME%\toolchain\avr8\avr8-gnu-toolchain\bin;^
%ATMEL_HOME%\toolchain\avr8\avrassembler;^
%PATH%

set CG=[91m
set CR=[92m
set CN=[0m
set cmd=atprogram -t atmelice -i ISP -d attiny13a program^
 --chiperase --flash --verify^
 --file "images\attiny\powerATtiny13.elf"

:loop
echo.
echo %cmd%
%cmd%

if %errorlevel% neq 0 goto :error

:success
echo %CR%SUCCESS%CN%
pause
goto :loop

:error
echo %CG%FAILED%CN%
sleep 2
goto :loop
