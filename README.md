# How to use?

Install requirements:

```shell
pip install -r requirements.txt
```

Install Graphviz: https://www.graphviz.org/download/

Generate data:

```shell
python process.py
```

Generate the graph using Graphviz:

```shell
dot -Tpng output/uni.dot -o output/uni.png
```
