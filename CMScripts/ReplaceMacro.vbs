'
'	This script updates build number in text file.
'	It replaces macro to value
'	passed as parameter
'
'	arguments:
'		- full qualified input file name
'		- full qualified output file name
'		- macro
'		- value

option explicit
on error resume next
if wscript.arguments.count < 4 then ShowUsageAndQuit

dim objFso, objFile, strText

Set objFSO = CreateObject("Scripting.FileSystemObject")
CheckError( "Can't create file system object" )

' read source file
set objFile = objFSO.OpenTextFile( wscript.arguments(0), 1 )
CheckError( "Can't open source file: " & wscript.arguments(0) )
strText = objFile.ReadAll()
CheckError( "Can't read from file: " & wscript.arguments(0) )
objFile.Close()
' perform replacment
dim regexp
set regexp = new RegExp
regexp.Pattern = wscript.arguments(2)
regexp.Global = true
strText = regexp.Replace( strText, wscript.arguments(3) )
' save result
set objFile = objFSO.CreateTextFile( wscript.arguments(1), true )
CheckError( "Can't open destination file: " & wscript.arguments(1) )
objFile.Write( strText )
CheckError( "Can't write into destination file: " & wscript.arguments(1) )
objFile.Close()

wscript.quit 0

Sub CheckError( strMsg )
	If err.number <> 0 Then
		wscript.echo "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~" & vbcrlf
		wscript.echo "Error: " & strMsg & vbcrlf
		wscript.echo "VBScript Error: " & hex(err.number) & ", " & err.description & vbcrlf
		wscript.echo "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~" & vbcrlf
		wscript.quit 1
	End If
End Sub

Sub ShowUsageAndQuit()
	wscript.echo "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~" & vbcrlf
	wscript.echo "Usage: cscript " & wscript.scriptname & "<input file> <output file> <macro> <value>" & vbcrlf
	wscript.echo "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~" & vbcrlf
	wscript.quit 1
End Sub
