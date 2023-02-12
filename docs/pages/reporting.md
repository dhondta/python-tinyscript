# Report Generation

## `Report` Class

The `Report` class is aimed to model a report document in an object-oriented fashion. It is a subclass of `list`, hence exposing the same methods. It also manages report elements' names for distinguishing elements in some particular output formats.

```python
from tinyscript.report import *

r = Report()
r.append(Text("test"))
r.append(List("item1", "item2", name="mylist")
```

!!! note "Free text"

    Note that free text can also be used. In this case, it will be handled as a `Text` element instance.

New elements can be:
    - Appended: `report.append(*elements)` ; note that, on the contrary of `list.append`, it can take multiple inputs.
    - Prepended: `report.prepend(*elements)`.
    - Inserted at position: `report.insert(integer, element)`.
    - Extending the report: `report.extend(list_of_elements)`.

!!! note "Header and footer"
    
    The `Header` and `Footer` elements can be added only once. Any additional instance is ignored.

And just like with the `list`, we can also `copy()` or `clear()` a `Report` instance. The `count` methods uses the element class name in lowercase to provide the counts of a type of elements.

-----

## Report Objects

Multiple report elements can be defined:

**Class** | **HTML tag** | **Description**
--- | --- | ---
`Blockquote(c)` | `blockquote` | Quoted text block, taking 1 argument: the [c]ontent
`Code(c)` | `pre` | Code block, taking 1 argument: the [c]ode
`Data(d)` |  | Data [d]ictionary ; its HTML is generated using [json2html](https://pypi.org/project/json2html/)
`Footer(l,c,r)` |  | Footer text for displaying on every page, split into 3 sections: [l]eft, [c]enter and [r]ight ; center's default is the page numbering (format: `#page/#pages`)
`Header(l,c,r)` |  | Header text for displaying on every page, split into 3 sections: [l]eft, [c]enter and [r]ight
`Image(s,d,w,h)` | `img` | Image reference, taking up to 4 arguments: the [s]ource and optionally a [d]escription, the [w]idth and the [h]eight
`List(*i)` | `ol`, `ul` | List of [i]tems that can be ordered or not
`Table(d,ch,rh,cf)` | `table` | Table with column and row headers, taking 3 arguments : a list of rows as the [d]ata, a list of [c]olumn [h]eaders, a list of [r]ow [h]eaders and a list of [c]olumn [f]ooters
`Text(c,t)` | `p` | Text paragraph, takin 1 argument : the [c]ontent to be displayed as a paragraph or any user-defined [t]ag
`Title(t)` | `h1` | Big bold title line, taking 1 argument : title's [t]ext
`Section(t)` | `h2` | Bold section title line, taking 1 argument : section title's [t]ext
`Subsection(t)` | `h3` | Bold section title line, taking 1 argument : subsection title's [t]ext

!!! note "Styling"
    
    All these elements can have the following styling keyword-arguments:
    
    - `size`: font size ; defaults to `12`
    - `color`: font color ; defaults to "`black`"
    - `style`: font style attribute (`bold`, `italic`, ...) ; default to "`normal`"
    
    Note that the aforementioned default values do not apply for particular size-dependent elements (e.g. `h1`, `h2`, ...) but using the size can still be forced by using the related keyword-argument.

!!! note "Element naming convention and assignment"
    
    Elements are named by default with their class name. Any single instance will have its element class name as its own name. If multiple instances of a class exist, the name is `class-id`, with the `id` being the index (starting at 1) of the element occurrence for this class. E.g. a report with 3 `Text` elements will have names, in the order of insertion, "`text-1`", "`text-2`" and "`text-3`". If this report has only 1 `List` element, this will be named "`list`" by default.
    
    This default behavior can of course be avoided by stating the name in the keyword-arguments of element's initialization. In this case, any other element from the same class initialized without a name will still have its name generated with its `id`. E.g. a report with 2 `Text` elements whose one with the name `mytable` will have its text elements named "`mytable`" and "`text-2`".

-----

## Output formats

The `Report` class aims to model a report for generating it to multiple common formats such as HTML or XML. The following formats are available:

- `csv`: this gathers all the data from `List` and `Table` elements to aggregate these into a single CSV.
- `html`: this generates the HTML version of the report.
- `json`: this collects all the data from the elements, by default in the form `{name: data}`, and `Data`'s `data` attribute (which is already in the JSON format).
- `md`: this generates the Markdown version of the report.
- `pdf` (only works with Python 3): this generates the PDF output of the report object with the filename set at `Report`'s object initialization or with its `filename` attribute (note that "`.pdf`" is appended by the output method).
- `xml`: this generates the XML version of the report, representing the data by using elements' names like with the `json` output format.

!!! note "Output indentation"
    
    For HTML and XML formats, the indentation can be set by using the `indent` keyword-argument. For HTML, the indentation defaults to 4 characters and for XML, it defaults to 2.
