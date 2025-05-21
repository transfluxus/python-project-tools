# Python tools

Can be installed with

`uv add git+https://github.com/transfluxus/python-project-tools@master[xml2yaml]`

or

`pip install git+https://github.com/transfluxus/python-project-tools`

or extras

`uv add git+https://github.com/transfluxus/python-project-tools@master[xml2yaml]`
or 
`uv pip install python-project-tools[xml2yaml]`

extras are: `xml2yaml`, `database`, `levenshtein`, `bags`

## root

`tools.env_root.root()` returns the root project path (`pathlib.Path`), which is where the .env file is located.

## package `pydantic_annotated_types`

provides `SerializableDatetime`, `SerializableDatetimeAlways`, `SerializablePath`
for pydantic models with Paths, or datetime, through PlainSerializer annotation.

## package files

read and write in several formats in a standardized form.