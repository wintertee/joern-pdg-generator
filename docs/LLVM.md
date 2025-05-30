# 基于IR的生成：LLVM

## LLVM IR

LLVM IR（Intermediate Representation，中间表示）是 LLVM 编译器基础设施项目的核心。它是一种低级的、静态单赋值（SSA）形式的语言，设计目标是成为高级语言和机器代码之间的通用桥梁。简单来说，它就像编译器内部使用的一种通用汇编语言，独立于特定的 CPU 架构。

LLVM 通过前端支持多种语言，包括Ada, C, C++, D, Delphi, Fortran, Haskell, Julia, Objective-C, Rust, Swift。

### 基于 LLVM IR 的 CFG / CallGraph 生成

参考：
- http://www.qfrost.com/posts/llvm/llvmopt-view-cfg/
- https://llvm.org/docs/tutorial/MyFirstLanguageFrontend/LangImpl05.html
- https://llvm.org/docs/CommandGuide/opt.html#cmdoption-opt-load

## MLIR (Multi-Level Intermediate Representation)

### 生态

MLIR 是 LLVM 项目团队近几年提出的新的多层级IR标准。生态非常热门，包括几个我们关心的方面：**HLS和电路设计**，**神经网络中间表示**。

- [CIRCT: Circuit Intermediate Representations (IR) Compilers and Tools](https://github.com/llvm/circt)

> CIRCT是一个基于LLVM中MLIR设计的一个开源EDA编译基础设施，试图构建一个统一硬件设计中间表示，为各个环节的EDA工具提供一套可重用可扩展的编译器基础设施

> 相关论文：[HLS from PyTorch to System Verilog with MLIR and CIRCT](https://capra.cs.cornell.edu/latte22/paper/2.pdf)

- [ONNX-MLIR](https://github.com/onnx/onnx-mlir)

> 为了表示神经网络模型，用户通常使用 Open Neural Network Exchange （ONNX），这是一种用于机器学习互作性的开放标准格式。ONNX-MLIR 是基于 MLIR 的编译器，用于将 ONNX 中的模型重写为可在不同目标硬件（如 x86 计算机、IBM Power Systems 和 IBM System Z）上执行的独立二进制文件。

> 相关论文：[Compiling ONNX Neural Network Models Using MLIR](https://arxiv.org/abs/2008.08272)

- [triton](https://github.com/triton-lang/triton)

> 代替CUDA的高级语言，基于Python和MLIR

其他项目详见：https://mlir.llvm.org/users/

### 基于 MLIR 的 CDFG 生成

类似LLVM IR，MLIR也提供了 CFG 的可视化：

参考：

- https://mlir.llvm.org/docs/Passes/#-view-op-graph
- https://mlir.llvm.org/doxygen/classmlir_1_1CallGraph.html
- https://llvm.org/devmtg/2023-05/slides/TechnicalTalks-May10/07-TomEccles-JeffNiu-MLIRDataflowAnalysis.pdf