# Universal Code Property Graph

## 介绍

Code Property Graph（CPG）最早由 Yamaguchi 等人在 2014 年提出，将 AST、CFG 和 DDG 融合为统一的图结构，并在 Joern 项目中实现并开源[^1]。目前 Joern 的 CPG 规范已迭代至 1.1 版本[^2]，并扩展了大量图属性。本项目旨在基于 Joern，为 Java 和 Python 代码生成文件级别的 CPG，包含 AST、CFG、DDG、调用图（Call Graph）和类型图（Type Graph）。

### Filter和Merge差异说明

`filter.py` 首先使用 `joern-export` 导出所有图，然后删除不需要的节点和边。 `merge.py` 则需要使用 `joern-export` 导出的 AST, CFG, DFG 进行合并，并使用 ALL 中的节点信息进行替换。

![iamge](assets/diff_filter_merge.png)

差别1：filter 出来的 CFG 要经过所有节点，merge 出来的 CFG 只经过语句节点。

差别2：filter 出来的 DDG 也是所有节点都有（从 argument 到 call），merge 出来的 DDG 只经过语句节点。

filter 出来的整体更细致、精度更高、更符合底层逻辑；merge 出来的 CFG、PDG 只出现在 AST 的高级节点中，不考虑子节点。

## 通用缺陷

- Call Graph 不支持operator overload
- Call Graph 不支持继承

## 语言支持情况

### Python

- [x] 对于Python类，会产生大量`<MetaClassAdapter>`, `<FakeNew>` 等和代码无关的方法。需要进行删除。

### Java

- [ ] Java文件中，如果main函数所在类没有定义构造函数，则会生成一个 `<init>` 节点，需要手动删除。另外，导出AST时，会缺少`TYPE_DECL`类型节点，导致AST缺少父节点，需要手动添加。

### C++

- C++支持较为完善，但是导出的图的细节上仍然和Java有区别。例如，在AST的`if control structure`中，其`code`属性包括整个代码块，而python中只包含`if`语句本身。

---

[^1]: Yamaguchi, Fabian, et al. "Modeling and discovering vulnerabilities with code property graphs." 2014 IEEE symposium on security and privacy. IEEE, 2014. [Joern 项目地址](https://github.com/joernio/joern)
[^2]: [Joern CPG 规范 1.1](https://cpg.joern.io/)