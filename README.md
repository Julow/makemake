# Makemake

Makefile generator

### Usage

To update the Makefile:

`make make`;

Create it:

```shell
curl -O https://raw.githubusercontent.com/Julow/makemake/master/makemake.py
python makemake.py
# It will prompt you for config
rm makemake.py
```

### Advenced config

The config is store at the top of the `Makefile`

Hidden config:
* `THREADS` Number of jobs to run simultaneously _(make -j)_ (Default: 1)
* `NICE_OUTPUT` (bool) Show only current compilation (Default: 1)
* `LD_CC` Compiler used to link the executable (Default: compiler used to build objs)

_Make sure the Makefile is ready by using `make make`_
