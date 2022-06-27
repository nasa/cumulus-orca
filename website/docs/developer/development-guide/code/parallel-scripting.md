---
id: parallel-scripting
title: Parallel Scripting
description: Instructions on running multiple functions in a script in Parallel.
---

[Parallel](https://www.gnu.org/software/parallel/man.html) is a means of running a function multiple times in different processes.
This can significantly increase the performance of scripts that loop with significant wait time.
For example, in cases with network calls such as package installation.

## Installation

For development, install via [brew](https://formulae.brew.sh/formula/parallel).

## Scripting Basics

Using parallel will run multiple instances of the command in different processes.
Standard output for each process will be buffered, and shown all at once when the process completes.
After all processes exit, execution of the main script will continue.
`$?` will contain how many tasks exited with a non-0 exit code.

#### Demo
- `--jobs 0` indicates that as many processes as possible should run at once.
- `-n 1` limits the number of parameters per process to 1.
- `-X` distributes the parameters among the new processes.
- `--halt now,fail=1` is used to halt all ongoing processes once 1 process exits with a non-0 exit code. Modifies `$?` to return the failing process' exit code instead of how many processes failed.
  :::tip
  Since the exit code does not indicate which process failed, logging for individual processes should be robust.
  :::

```bash
parallel --jobs 0 -n 1 -X --halt now,fail=1 function_name ::: $parameter_array
process_return_code=$?
if [ $process_return_code -ne 0 ]; then
  echo "ERROR: process failed with code $process_return_code."
  failure=1
fi
```

## Alternatives
Some alternatives were researched, but found to be more limited.

### Background and Wait (&)
If a function is run with a `&` suffix, it will start in a new process.
The process ID can then be captured, and used to track progress and exit codes.

#### Cons
- Requires extra code for managing processes.
- Logging is not grouped by function invocation.

#### Demo
```bash
declare -A pids
for param in $parameter_array
do
function_name $param &
pids[${param}]=$!  # This assumes that all parameters are unique.
done

failure=0
for param in "${!pids[@]}"
do
  wait ${pids[$param]}
  process_return_code=$?
  if [ $process_return_code -ne 0 ]; then
    echo "ERROR: $param failed."
    failure=1
  fi
done
```

### [Xargs](https://www.man7.org/linux/man-pages/man1/xargs.1.html)
Xargs has several useful performance optimization parameters, but is more difficult to use.

#### Cons
- Logging is not grouped by function invocation.
- Parameters are passed in via a single string, split on a separator character, which is rather brittle.
- Exit codes are not passed out to main process.

#### Demo
```bash
echo "${parameter_array[@]}" | xargs -n 1 -P 0 bash -c 'function_name "$@"' _
```
