

class AttributeDict(dict):

    """
    Dict which holds the result values

The result dict comes from the *parse* function from the ConfigValidator class.

```python
ConfigValidator.parse(config_dict, feature_key="__feature__")
```
The first parameter *config_dict* is the configuration that is usesed to generate the result dict. 
With the parameter *feature_key* the dict key for features for sections is overriden. 

The result is a normal python dict what can also accessed by dot notation. 
```python
assert res["SectionA"]["option1"] == res.SectionA.option1
```

    remark: The result for the feature for section depends on the used feature.
    remark: So maybe the resulting structure is not an default dict.

    """

    def __getattr__(self, name):
        """
        TODO
        """
        val = self[name]
        if isinstance(val, AttributeDict):
            return AttributeDict(val)
        elif isinstance(val, dict):
            return AttributeDict(val)
        else:
            return val

    def get(self, section, option):
        """
        TODO
        """
        return self[section][option]
