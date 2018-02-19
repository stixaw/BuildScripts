@echo off
rem set EPOCROOT=C:\Symbian\9.1\S60_3rd

call patchsdk.bat

rem
rem Delete outputs from the previous build.
rem
call sas_clean

rem
rem Generate the .pkg files.
rem
call generate_pkg_files

call build_pc_stuff

rem
rem Build WINS version of SSS
rem
call sas_emulator_build_91s60
call sas_emulator_build_91uiq

rem
rem Build ARM version of SAS
rem
call sas_build_91s60
call sas_build_91uiq

if not "%1"=="noloc" (
	rem
	rem Do localization build. This rebuilds the installers
	rem and does the layout.
	rem
	echo ***** Start Localization Build *****
	pushd ..\Localization\cm
	call do_lang_build
	popd
	echo ***** End Localization Build *****
	goto verify_deliverables
)

rem
rem Create the layout (if it wasn't done above by the loc build).
rem
call do_layout.bat

:verify_deliverables
set /a missingcount=0

for %%f in (deliverables.txt *.lst) do call verify_deliverables.bat %%f
if not "%missingcount%"=="0" goto deliverables_missing

rem
rem Woot
rem
goto we_are_done

:deliverables_missing
echo Error: %missingcount% deliverables missing - build failed
set missingcount=
exit /b 1

rem
rem goto label for ending the batch job with success
rem
:we_are_done
md c:\output_msi
xcopy C:\bld_area\SymMS_6.0\Symbian\cm\layout\sym_prod_sepme_corp\English\*.* c:\output_msi\English /C /I /V /Y /R /K /S /E
set missingcount=
exit /b 0