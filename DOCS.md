# Documentation

## Optree blocks

### The if block

#### Description

Compares A and B values based of input options provided and passes a boolean value based on the operation input to blocks under outputtrue if True or the blocks under outputfalse is False. The can take an input from a parent block which is the for the A value (third preference).

#### Inputs

_valuea_: a value of any type to be used for A (first preference)  
_variablea_: the value of the variable with this name will be used for A (second preference)  
_valueb_: a value of any type to be used for B (first preference)  
_variableb_: the value of the variable with this name will be used for B (second preference)  
_operation_:  the operation to do on A and B

#### Example

```
{
	"function": "if",
	"operation": "=",
	"variableb": 0,
	"outputtrue":
	{

	},
	"outputfalse":
	{

	}
}
```

### The setvariable block

Takes in an A and B input and returns a boolean baseon the operation input.

#### Inputs

_name_:  
_value_:  

#### Example

```
{
	"function": "setvariable",
	"name": "state",
	"value": "up",
	"output":
	{
	}
}
```

### The variablereset block

#### Inputs

_name_:  

#### Example

```
{
	"function": "variablereset",
	"name": "count",
	"output":
	{
	}
}
```

### The variableincrease block

#### Inputs

_name_:  

#### Example


```
{
	"function": "variableincrease",
	"name": "count",
	"output":
	{
	}
}
```

### The variabledecrease block

#### Inputs

_name_:  

#### Example


```
{
	"function": "variabledecrease",
	"name": "count",
	"output":
	{
	}
}
```

### The log block

#### Inputs

_message_:  

#### Example


```
{
	"function": "log",
	"message": "Result was false",
	"output":
	{
	}
}
```

### The ping block

#### Inputs

_targetaddress_:  
_targetvariable_:  

#### Example


```
{
	"function": "ping",
	"targetaddress": "192.168.27.3",
	"output":
	{
	}
}
```

### Example webhook block

#### Inputs

_url_:  
_poat_:  

#### Example

```
{
	"function": "webhook",
	"url": "https://discord.com/api/webhooks/...",
	"post": 
	{
		"content": "Test message"
	},
	"output":
	{
	}
}
```