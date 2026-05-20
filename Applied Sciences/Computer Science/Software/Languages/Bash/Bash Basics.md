---
title: "Bash Basics Cheat Sheet"
domain: "Applied Sciences"
subdomain: "Computer Science > Languages > Bash"
tags: [sciences-appliquées, informatique, bash]
date: "2026-02-16"
---

# Bash Basics Cheat Sheet

Bash, or the **Bourne Again SHell**, is a Unix shell and command language that is widely used for scripting and automation on Linux and macOS systems. Below is a quick reference to help you get started with basic Bash commands and scripting.

## 1. Basics of Bash Commands

### Syntax
- **Command format**: `<command> [option] [arguments]`
- **Example**: `ls -l /home/user`

### Basic Commands
| Command  | Description                               |
|----------|-------------------------------------------|
| `ls`     | List directory contents                  |
| `cd`     | Change directory                         |
| `pwd`    | Print current directory                  |
| `mkdir`  | Create a new directory                   |
| `rm`     | Remove files or directories              |
| `cp`     | Copy files or directories                |
| `mv`     | Move or rename files or directories      |
| `echo`   | Display text or variables                |
| `cat`    | Concatenate and display file contents    |
| `touch`  | Create a new empty file                  |

### File Permissions
- View permissions: `ls -l filename`
- Change permissions: `chmod [permissions] filename`
  - Examples: 
    - `chmod +x script.sh` - make executable
    - `chmod 755 filename` - set specific permissions

## 2. Variables and Environment

### Defining Variables
- Syntax: `variable_name=value`
  ```bash
  name="John Doe"
  echo $name
  ```

### Environment Variables
- **Setting an environment variable**: `export VAR=value`
- **Accessing variables**: `$VAR`
- Common environment variables:
  - `$HOME` - User home directory
  - `$PATH` - Directories Bash looks in to find executables

### Special Variables
| Variable  | Description                        |
|-----------|------------------------------------|
| `$0`      | Script name                        |
| `$1` to `$9` | Positional arguments (1 to 9) |
| `$#`      | Number of arguments                |
| `$@`      | All arguments as a list            |
| `$?`      | Exit status of last command        |
| `$$`      | Process ID of current shell        |

## 3. Basic Control Structures

### Conditional Statements
```bash
if [ condition ]; then
  # commands
elif [ condition ]; then
  # commands
else
  # commands
fi
```

- **Example**:
  ```bash
  if [ $age -ge 18 ]; then
    echo "You are an adult."
  else
    echo "You are not an adult."
  fi
  ```

### Cases
- **Example:**
```bash
read -p "Enter a choice (start, stop, restart): " action

case "$action" in
  start)
    echo "Starting service..."
    # Commands to start the service
    ;;
  stop)
    echo "Stopping service..."
    # Commands to stop the service
    ;;
  restart)
    echo "Restarting service..."
    # Commands to restart the service
    ;;
  *)
    echo "Invalid option"
    ;;
esac

```
### Loops

#### For Loop
```bash
for var in list; do
  # commands
done
```

- **Example**:
  ```bash
  for i in {1..5}; do
    echo "Number $i"
  done
  ```

#### While Loop
```bash
while [ condition ]; do
  # commands
done
```

- **Example**:
  ```bash
  count=1
  while [ $count -le 5 ]; do
    echo "Count is $count"
    count=$((count + 1))
  done
  ```

## 4. Functions

Functions in Bash allow for reusable pieces of code.

### Defining a Function
```bash
function_name() {
  # commands
}
```

### Calling a Function
```bash
function_name
```

- **Example**:
  ```bash
  greet() {
    echo "Hello, $1!"
  }
  
  greet "Alice"  # Output: Hello, Alice!
  ```

## 5. Basic I/O Redirection

### Redirect Output
- **Redirect standard output**: `command > file`
- **Append to file**: `command >> file`
- **Redirect standard error**: `command 2> file`
- **Redirect both standard output and error**: `command &> file`

### Piping
- Use `|` to pass output of one command to another.
  ```bash
  ls -l | grep "file.txt"
  ```

## 6. Basic String Operations

### String Comparison
```bash
if [ "$str1" = "$str2" ]; then
  echo "Strings are equal."
fi
```

### String Length
```bash
length=${#str}
```

### Substring Extraction
```bash
substr=${str:position:length}
```

- **Example**:
  ```bash
  str="Hello, World!"
  echo ${str:7:5}  # Output: World
  ```

## 7. Common Expressions

### Arithmetic Operations
Use `(( ))` for arithmetic operations.
```bash
result=$((5 + 3))
echo $result  # Output: 8
```

### Logical Operators
| Operator | Description   |
|----------|---------------|
| `-eq`    | Equal         |
| `-ne`    | Not equal     |
| `-gt`    | Greater than  |
| `-lt`    | Less than     |
| `-ge`    | Greater/equal |
| `-le`    | Less/equal    |

### File Operations
| Test                | Description                     |
|---------------------|---------------------------------|
| `-e filename`       | File exists                    |
| `-f filename`       | Regular file                   |
| `-d dirname`        | Directory exists               |
| `-r filename`       | File is readable               |
| `-w filename`       | File is writable               |
| `-x filename`       | File is executable             |

## 8. Writing Simple Scripts

To create and run a Bash script:

1. **Create a new file**:
   ```bash
   nano script.sh
   ```

2. **Add the shebang** to indicate the script uses Bash:
   ```bash
   #!/bin/bash
   ```

3. **Write your script** and save.

4. **Make it executable**:
   ```bash
   chmod +x script.sh
   ```

5. **Run the script**:
   ```bash
   ./script.sh
   ```

## 9. Sample Script

Here’s a simple script that greets the user with the current date:

```bash
#!/bin/bash

# Greet the user
echo "Hello, $(whoami)! Today is $(date +"%A, %B %d, %Y")."
```
