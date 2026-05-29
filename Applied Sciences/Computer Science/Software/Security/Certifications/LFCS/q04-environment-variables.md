# Question 4 — Environment Variables

## Énoncé

Solve this question on: `terminal`

There is an existing env variable for user `candidate@terminal`: `VARIABLE1=random-string`, defined in file `.bashrc`. Create a new script under `/opt/course/4/script.sh` which:
1. Defines a new env variable `VARIABLE2` with content `v2`, only available in the script itself
2. Outputs the content of the env variable `VARIABLE2`
3. Defines a new env variable `VARIABLE3` with content `${VARIABLE1}-extended`, available in the script itself and all child processes of the shell as well
4. Outputs the content of the env variable `VARIABLE3`

> ℹ️ Do not alter the `.bashrc` file, everything needs to be done in the script itself

## Solution

Well, let's check the existing variable and its content as mentioned:
```bash
echo $VARIABLE1
random-string
env | grep VARIABLE
VARIABLE1=random-string
```

How the variable's value defined? Let's check the `.bashrc` file:
```bash
cat .bashrc | grep VARIABLE1
export VARIABLE1=random-string
```

Now let's create a script which will define a new env variable called `VARIABLE2` with content `v2`:
```bash
vim /opt/course/4/script.sh
VARIABLE2="v2"
echo $VARIABLE2
```

We give it a try, it should output the variable content, but shouldn't make it available (export) afterwards:
```bash
bash /opt/course/4/script.sh
v2
```

Finally, we define the third environment variable called `VARIABLE3` within the same script

VARIABLE2="v2"

echo $VARIABLE2

export VARIABLE3="${VARIABLE1}-extended"    # add

echo $VARIABLE3                             # add

Run and check the result
```bash
sh /opt/course/4/script.sh
v2
random-string-extended
```

What's the difference between export and not using export? Let's demonstrate it:
```bash
TEST1=test1
export TEST2=test2
echo $TEST1
test1
echo $TEST2
test2
bash
echo $TEST1 # variable NOT available in subprocesses
echo $TEST2 # exported variable available in subprocesses
test2
```
