## Common argument types

While adding arguments to the parser (relying on `argparse`), Tinyscript provides some useful type validation functions that can be used with the `type` keyword argument, namely (returning `ValueError` when the validation fails):

- `file_exists`: existing file path
- `files_list`: list of only existing file paths
- `files_filtered_list`: list of at least one existing file path (bad paths are filtered)
- `folder_exists`: existing folder
- `ints`: list of integers
- `neg_int`, `negative_int`, `neg_ints`, `negative_ints`: single negative integer or list of negative integers
- `pos_int`, `positive_int`, `pos_ints`, `positive_ints`: single positive integer or list of positive integers
- `ip_address`, `ip_address_list`: valid IP address (IPv4 or IPv6) or list of IP addresses ; returns the result of `ipaddress.ip_address`
- `ip_address_network`: valid IP address network (e.g. `192.168.1.0/24`) ; returns the result of `ipaddress.ip_network`
- `port_number`: valid port number
- `port_number_range`: valid list of port numbers, ranging from and to the given bounds

-----

## Type checking functions

According to the DRY philosophy, Tinyscript provides some type checking functions:

- `is_int` / `is_pos_int` / `is_neg_int`: 
- `is_lst`: 
- `is_str`: 
- `is_lambda`: 

-----

## Data type tranformation functions

Tinyscript also provides a series of intuitive data transformation functions, formatted as follows:

```
[input_data_type_trigram]2[output_data_type_trigram]
```

The currently supported functions are:

- `bin2int` / `int2bin`
- `bin2str` / `str2bin`
-----

## Useful constants


