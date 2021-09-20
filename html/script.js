loadData = async (file) => {
  const res = await fetch(file);
  const data = await res.json();
  return data;
};

loadDataText = async (file) => {
  const res = await fetch(file);
  const data = await res.text();
  return data;
};

window.addEventListener("DOMContentLoaded", async (event) => {
  const nodesMap = new Map();
  const nodes = [];
  const constraints = [
    {
      type: "alignment",
      axis: "y",
      offsets: [],
    },
  ];

  d3.csv("input.csv", (data) => {
    data.forEach((row, idx) => {
      // skip header
      if (idx > 0) {
        nodesMap.set(row.fio, { ...row, index: idx - 1 });
        nodes.push({
          ...row,
          width: Math.max(50, row.fio.length * 7),
          height: 40,
        });
        constraints[0].offsets.push({
          node: idx - 1,
          offset: (row.year - 2000) * 100,
        });
      }
    });

    const links = [];
    nodes.forEach((node, idx) => {
      if (node.parent.length > 0) {
        const parentIdx = nodesMap.get(node.parent).index;
        links.push({ source: idx, target: parentIdx });
      }
    });

    var width = 3000,
      height = 1500;

    var color = d3.scaleOrdinal(d3.schemeCategory20);

    var c = cola
      .d3adaptor(d3)
      .flowLayout("y", 200)
      .linkDistance(200)
      .avoidOverlaps(true)
      .size([width, height]);

    var svg = d3
      .select("body")
      .append("svg")
      .attr("width", width)
      .attr("height", height);

    c.nodes(nodes).links(links).constraints(constraints).start();

    var link = svg
      .selectAll(".link")
      .data(links)
      .enter()
      .append("line")
      .attr("class", "link");

    var node = svg
      .selectAll(".node")
      .data(nodes)
      .enter()
      .append("rect")
      .attr("class", "node")
      .attr("width", function (d) {
        return d.width;
      })
      .attr("height", function (d) {
        return d.height;
      })
      .attr("rx", 5)
      .attr("ry", 5)
      .style("fill", function (d) {
        return color(1);
      })
      .call(c.drag);

    var label = svg
      .selectAll(".label")
      .data(nodes)
      .enter()
      .append("text")
      .attr("class", "label")
      .text(function (d) {
        return `${d.fio}`;
      })
      .call(c.drag);

    node.append("title").text(function (d) {
      return `${d.fio}`;
    });

    c.on("tick", function () {
      link
        .attr("x1", function (d) {
          return d.source.x;
        })
        .attr("y1", function (d) {
          return d.source.y;
        })
        .attr("x2", function (d) {
          return d.target.x;
        })
        .attr("y2", function (d) {
          return d.target.y;
        });

      node
        .attr("x", function (d) {
          return d.x - d.width / 2;
        })
        .attr("y", function (d) {
          return d.y - d.height / 2;
        });

      label
        .attr("x", function (d) {
          return d.x;
        })
        .attr("y", function (d) {
          var h = this.getBBox().height;
          return d.y + h / 4;
        });
    });
  });
});