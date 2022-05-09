# numpad

A programming language that can be written with just the numpad, for when you're also eating a sandwich.

Numpad is made up of statements, each of which takes up a single line of code. The type of statement a line contains can usually be determined by first character of the line. The language is designed to manipulate integers and Pythonic lists. It can only operate on objects like floating-point numbers and strings abstractly.

## Variables

A variable is notated by an asterisk `*` followed by some number. For example, `*1`, `*1402`, and `*01` are all separate variables.

Variables that start with a `0`, like `*01`, act as function arguments, sequentially in the order they are passed to the function. The exception is `*00`, which acts as a return value for the function; the final value for this variable will be returned.

## Types of Statements

### Assignment Statement

A line that begins with the `*` character and contains the `.` character but does not **end** with '.' is an assignment statement. This statement consists of a variable name, then the `.`, then some expression.

After the line is executed, the value of the LHS variable is the result of the evaluated RHS expression.

For example, the following code sets the variable `*4` to double the parameters `*01`, and then sets the return value to the result.

```
*4.*01*2
*00.*4
```

### Definition Statement

A line that begins with the `*` character and **ends** with the `.` character is a function-definition statement.

Statements contained within the function definition will be carried out when the function is called.

A function definition is closed by a single blank line.

#### Parameter List

The first line(s) of a function definition must provide the parameter list. Any number of lines of the format `[PARAM]..[VALUE]` can be written here, where `PARAM` and `VALUE` are both number values. These lines assign default values for the parameters listed.

After any default values are set for a parameter, a final line of the format `[TOTAL].`, where `TOTAL` is a number, sets the accepted total number of parameters for this function.

For example, the following code defines a function `*5171` with two parameters, the second defaulting to `1` when no argument is given. Note that the last line is empty (the `.` acts as whitespace) so the function is complete.

```
*5171.
.2..1
.2.
.
```
