# 文明研究实验室（civilization-lab）

这是一个用来记录、整理和讨论政治、经济、文化、宗教、地理、历史等问题的个人知识库。

## 组织原则

本仓库按三种主要研究方向组织：

- [`domains/`](domains/README.md)：按学科或领域沉淀可复用的基础知识、概念、机制和理论。
- [`topics/`](topics/README.md)：围绕具体问题进行跨领域讨论，形成论证、比较和阶段性结论。
- [`cases/`](cases/README.md)：记录具体国家、文明、事件和比较案例，用现实过程检验理论。

简单说：领域回答“有哪些可复用的知识”，议题回答“多个方面如何共同解释一个问题”，案例回答“具体发生了什么”。

[`sources/`](sources/README.md) 提供资料与证据，[`methods/`](methods/README.md) 提供研究方法。尚未整理的念头先放进 [`inbox/`](inbox/README.md)，不要因为一开始无法准确分类而放弃记录。

## 当前目录

```text
civilization-lab/
├─ domains/                 # 单领域知识
│  ├─ politics/            # 政治
│  ├─ economics/           # 经济
│  ├─ military/            # 军事
│  ├─ culture/             # 文化（含宗教与哲学）
│  ├─ geography/           # 地理
│  └─ history/             # 历史
├─ topics/                  # 跨领域议题
│  ├─ rise-and-fall-of-states/
│  ├─ economic-cycles/
│  ├─ geography-and-states/
│  └─ religion-culture-and-states/
├─ cases/                   # 国家、文明、事件与比较案例
├─ methods/                 # 比较、因果与史料分析方法
├─ inbox/                   # 未归类的想法和问题
├─ sources/                 # 书籍、论文、数据等资料卡片
└─ templates/               # 笔记模板
```

## 怎么记录

1. 一个短想法暂时拿不准放哪，就写进 `inbox/`。
2. 某个领域内通用的概念或规律，整理进对应的 `domains/<领域>/`。
3. 一个需要多种视角回答的问题，在 `topics/<议题>/` 建立议题主页。
4. 围绕具体国家、文明或事件的完整过程，整理进 `cases/`。
5. 领域、议题和案例笔记用相对链接互相引用，不重复抄写整段内容。
6. 区分事实、他人观点、自己的推测，并给可核查内容标注来源。

讨论时不要求参与者预先判断内容属于哪个方向。先自然讨论，由 AI 助手在适合沉淀时根据内容选择归属，并说明写入了哪里。

文件和目录使用稳定的英文 `kebab-case` 名称，正文与标题使用中文。新建内容时可复制 [`templates/`](templates/) 中的模板。

具体的提问、论证、质疑和结论沉淀方式见 [`AGENTS.md`](AGENTS.md)。
