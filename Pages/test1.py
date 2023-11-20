import streamlit as st
from streamlit_echarts import st_echarts
import pandas as pd

# 设置页面布局为宽屏模式，充满整个屏幕宽度
st.set_page_config(layout="wide", page_icon=None,
                   initial_sidebar_state="collapsed", page_title=None)

links_df = pd.read_csv('Dataset/Links.csv')
nodes_df = pd.read_csv('Dataset/Nodes.csv')

# Create a dictionary that maps node IDs to their types using the Nodes.csv data
node_types = nodes_df.set_index('id')['type'].to_dict()

# Extract unique nodes and link types
all_nodes = set(links_df['source']).union(set(links_df['target']))
link_types = links_df['type'].unique()

# Hardcode the specified node IDs
special_node_ids = ["Mar de la Vida OJSC", "979893388", "Oceanfront Oasis Inc Carriers", "8327"]

# Set up columns for layout
left_column, mid_column,right_column = st.columns([1, 4, 1.5])

# Sidebar for selecting nodes and link types
node_categories = nodes_df['type'].unique()  # Assuming 'type' column has the categories
# 默认选中所有类别
selected_categories = set(node_categories)

selected_nodes = []
with left_column:
    st.subheader("Quick Select Suspect")
    for node_id in special_node_ids:
        if st.checkbox(node_id, key=node_id):
            selected_nodes.append(node_id)

    st.subheader("Search Node By ID")
    node_query = st.text_input("Node ID", key="node_search")
    if node_query:
        selected_nodes.append(node_query)

    selected_link_types = set()
    st.subheader("Link Type")
    for link_type in link_types:
        if st.checkbox(link_type, key=f"link_type_{link_type}", value=True):
            selected_link_types.add(link_type)

    st.subheader("Node Type")
    for category in node_categories:
        # 使用default=True使复选框默认被选中
        if st.checkbox(category, key=f"category_{category}", value=True):
            selected_categories.add(category)
        else:
            selected_categories.discard(category)  # 如果用户取消选中，则从集合中移除

# Function to get neighbors
def get_neighbors(selected_nodes, links_df, selected_link_types, selected_categories):
    neighbors = set()
    for node in selected_nodes:
        if node_types[node] in selected_categories:  # Check if node is in selected categories
            filtered_df = links_df[links_df['type'].isin(selected_link_types)]
            neighbors.update(filtered_df[filtered_df['source'] == node]['target'].tolist())
            neighbors.update(filtered_df[filtered_df['target'] == node]['source'].tolist())
    return neighbors.union(set(selected_nodes))

# Define the colors for each node type
category_colors = {
    "person": "#df493f",
    "political_organization": "#f9d580",
    "organization": "#e4a2b8",
    "event": "#54beaa",
    "company": "#fcf1f0",
    "location": "#b0d992",
    "vessel": "#99b9e9",
    "movement": "#af8fd0",
    "Uncategorized": "#eca680"
}


# Main area for displaying the graph
with mid_column:
    if selected_nodes and selected_link_types and selected_categories:
        neighbors_set = get_neighbors(selected_nodes, links_df, selected_link_types, selected_categories)
        filtered_df = links_df[(links_df['source'].isin(neighbors_set)) & (links_df['target'].isin(neighbors_set)) & (links_df['type'].isin(selected_link_types))]

        echarts_nodes = [
            {
                "name": node,
                "symbolSize": 10 if node in special_node_ids else 5,  # Increase size for special nodes
                "draggable": True,
                "category": node_types.get(node, "Unknown"),
                "symbol": 'rect' if node in special_node_ids else 'circle',  # Set shape to star for special nodes
            } 
            for node in neighbors_set
        ]

        echarts_links = filtered_df.apply(
            lambda row: {"source": row['source'], "target": row['target'], "value": row['type']},
            axis=1
        ).tolist()

        # 定义不同类别的节点样式
        categories = [
            {"name": "person", "itemStyle": {"color": "#df493f"}},
            {"name": "political_organization", "itemStyle": {"color": "#f9d580"}},
            {"name": "organization", "itemStyle": {"color": "#e4a2b8"}},
            {"name": "event", "itemStyle": {"color": "#54beaa"}},
            {"name": "company", "itemStyle": {"color": "#fcf1f0"}},
            {"name": "location", "itemStyle": {"color": "#b0d992"}},
            {"name": "vessel", "itemStyle": {"color": "#99b9e9"}},
            {"name": "movement", "itemStyle": {"color": "#af8fd0"}},
            {"name": "Uncategorized", "itemStyle": {"color": "#eca680"}}
        ]


        # ECharts directed graph configuration
        option = {
            "backgroundColor": '#FFFFFF',  # 设置背景色为白色
            "tooltip": {},
            "legend": {
                "data": list(map(lambda c: c['name'], categories)),
                "selectedMode": True  # 禁止legend的默认点击行为
            },
            "series": [
                {
                    "type": "graph",
                    "layout": "force",
                    "symbolSize": 10,
                    "focusNodeAdjacency": True,
                    "roam": "scale",
                    "draggable": True,
                    "focusNodeAdjacency": True,  # 当点击一个节点时，高亮显示与其相连的边和节点
                    "label": {
                        "show": True,
                        "position": 'right',  # 可以根据实际情况调整标签位置
                        "color":"black" #设置节点文字颜色
                    },
                    "categories": categories,
                    "edgeSymbol": ["none", "arrow"],
                    "edgeSymbolSize": [0, 10],# 根据需要调整箭头的大小
                    "nodes": echarts_nodes,
                    "links": echarts_links,
                    "lineStyle": {
                        "opacity": 0.9,
                        "width": 2,
                        "curveness": 0.1
                    },
                    # 在这里增加了一个itemStyle属性来增加节点的大小
                    "itemStyle": {
                        "normal": {
                            "borderWidth": 0,  # 设置边框宽度，用于放大效果
                            "borderColor": '#fff'
                        }
                    }
                }
            ],

            "graphic": [
                {
                    "type": "rect",
                    "z": 100,
                    "left": 'center',
                    "top": 'center',
                    "shape": {
                        "width": 1000,  # 画布宽度
                        "height": 1000  # 画布高度
                    },
                    "style": {
                        "fill": 'none',
                        "shadowBlur": 10,
                        "shadowOffsetX": 5,
                        "shadowOffsetY": 5,
                        "shadowColor": 'rgba(0,0,0,0.3)'
                    }
                }
            ]
        }

        # Display the graph using streamlit_echarts
        st_echarts(options=option, height="1000px")

with right_column:
    st.subheader("Edeg Statistics")

    # Calculate the count of each link type in the filtered graph
    link_type_counts = filtered_df['type'].value_counts().reset_index()
    link_type_counts.columns = ['type', 'count']

    # Prepare data for ECharts pie chart
    pie_data = [
        {"value": count, "name": link_type}
        for link_type, count in zip(link_type_counts['type'], link_type_counts['count'])
    ]

    # ECharts pie chart configuration
    pie_option = {
        "tooltip": {
            "trigger": 'item',
            "formatter": "{a} <br/>{b}: {c} ({d}%)"
        },
        "legend": {
            "orient": 'vertical',
            "left": 'left',
        },
        "series": [
        {
            "name":'Edeg Statistics',
            "type": 'pie',
            "radius": '50%',
            "data": pie_data,
            "avoidLabelOverlap": True,
            "label": {
                "show": False,  # Set to False to hide labels on the pie sectors
                "position": 'outside',
            },
            "emphasis": {
                "itemStyle": {
                    "shadowBlur": 10,
                    "shadowOffsetX": 0,
                    "shadowColor": 'rgba(0, 0, 0, 0.5)'
                }
            }
        }
    ]
    }

    # Display the pie chart
    st_echarts(options=pie_option, height="400px")

    #统计节点数量的扇形图
    st.markdown("---")
    st.subheader("Node Statistics")

    # Calculate the count of each node type in the filtered graph
    node_type_counts = nodes_df[nodes_df['id'].isin(neighbors_set)]['type'].value_counts().reset_index()
    node_type_counts.columns = ['type', 'count']

    # Prepare data for ECharts pie chart based on node statistics
    node_pie_data = [
        {
            "value": count,
            "name": node_type,
            "itemStyle": {"color": category_colors.get(node_type, "#000000")}  # Default to black if not found
        }
        for node_type, count in zip(node_type_counts['type'], node_type_counts['count'])
    ]

    # ECharts pie chart configuration for node statistics
    node_pie_option = {
        "tooltip": {
            "trigger": 'item',
            "formatter": "{b}: {c} ({d}%)"
        },
        "legend": {
            "orient": 'vertical',
            "left": 'left',
        },
        "series": [
            {
                "name": 'Node Statistics',
                "type": 'pie',
                "radius": '50%',
                "data": node_pie_data,
                "avoidLabelOverlap": True,
                "center": ['60%', '50%'],  # Adjust the '60%' as needed to move the chart to the right
                "label": {
                    "show": False,  # Set to False to hide labels on the pie sectors
                    "position": 'outside',
                },
                "emphasis": {
                    "itemStyle": {
                        "shadowBlur": 10,
                        "shadowOffsetX": 0,
                        "shadowColor": 'rgba(0, 0, 0, 0.5)'
                    }
                }
            }
        ]
    }

    # Display the node statistics pie chart
    st_echarts(options=node_pie_option, height="400px")
