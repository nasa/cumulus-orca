cd ..
$repoDir = Get-Location
$tasks = 
[TaskInfo]::new("copy_from_archive", "copy_from_archive.py"),
[TaskInfo]::new("copy_to_archive", "handler.py"),
[TaskInfo]::new("db_deploy", "db_deploy.py"),
[TaskInfo]::new("extract_filepaths_for_granule", "extract_filepaths_for_granule.py"),
[TaskInfo]::new("request_files", "request_files.py"),
[TaskInfo]::new("request_status", "request_status.py")

foreach ($task in $tasks){
    cd "$repoDir\tasks\$($task.Name)"

    "Running for $($task.Name)\$($task.PrimaryFile)"

    venv\Scripts\activate
    $docs = python -m pydoc $([IO.Path]::GetFileNameWithoutExtension($task.PrimaryFile))
    deactivate
    
    # Remove the last 6 lines that contain the local file path and whitespace.
    $docs = $docs[0..($docs.Count - 6)]

    Set-Content -Path "$repoDir\website\docs\developer\code\lambda_docs\$($task.Name).md" -Value $docs
}

Class TaskInfo
{
    [String] $Name
    [String] $PrimaryFile
    TaskInfo([String] $name, [String] $primaryFile)
    {
        $this.Name = $name
        $this.PrimaryFile = $primaryFile
    }
}