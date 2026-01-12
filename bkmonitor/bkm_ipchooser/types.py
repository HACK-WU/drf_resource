import typing

Scope = dict[str, int | str]

ScopeList = list[Scope]

MetaData = Scope

TreeNode = dict[str, typing.Any]

ReadableTreeNode = dict[str, typing.Any]

HostInfo = dict[str, typing.Any]

FormatHostInfo = dict[str, typing.Any]

Condition = dict[str, int | str | typing.Iterable]

Template = dict[str, typing.Any]

TemplateNode = dict[str, typing.Any]

DynamicGroup = dict[str, typing.Any]
