import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from io import StringIO, BytesIO
from datetime import datetime, date, timedelta
import base64

# App title and configuration
st.set_page_config(page_title="Lab Assistant Pro", layout="wide")
st.title("🧪 Advanced Wet Lab Assistant")
st.markdown("""
A comprehensive toolkit for biochemistry lab calculations, experiment documentation, and protocol generation.
""")

# Initialize session states
if 'experiment_data' not in st.session_state:
    st.session_state.experiment_data = pd.DataFrame(columns=[
        'Experiment', 'Date', 'Component', 'Concentration', 
        'Volume', 'Notes'
    ])

if 'protocol_steps' not in st.session_state:
    st.session_state.protocol_steps = []

if 'plot_data' not in st.session_state:
    st.session_state.plot_data = pd.DataFrame(columns=['x', 'y', 'series'])

if 'daily_tasks' not in st.session_state:
    st.session_state.daily_tasks = pd.DataFrame(columns=['Date', 'Task', 'Priority', 'Status'])

# Create tabs for different functionalities
tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8 = st.tabs([
    "Dilution Calculator", 
    "Solution Preparation", 
    "Buffer Calculator",
    "Daily Lab Planner",
    "Experiment Log", 
    "Protocol Generator",
    "Data Visualization",
    "Data Export"
])

# Common unit selections for reuse
conc_units = ["M", "mM", "µM", "nM", "g/L", "mg/mL", "%"]
vol_units = ["L", "mL", "µL"]
buffer_types = ["Tris-HCl", "PBS", "TAE", "TBE", "HEPES", "Custom"]
priority_levels = ["High", "Medium", "Low"]

# ===== TAB 1: DILUTION CALCULATOR =====
with tab1:
    st.header("Dilution Calculator")
    
    col1, col2 = st.columns(2)
    with col1:
        c1 = st.number_input("Initial concentration (C1)", min_value=0.0, value=1.0)
        v1 = st.number_input("Initial volume (V1)", min_value=0.0, value=1.0, format="%.2f")
        unit_c = st.selectbox("Concentration unit", conc_units)
    
    with col2:
        c2 = st.number_input("Final concentration (C2)", min_value=0.0, value=0.1)
        v2 = st.number_input("Final volume (V2)", min_value=0.0, value=10.0, format="%.2f")
        unit_v = st.selectbox("Volume unit", vol_units)
    
    # Calculate missing parameter
    if st.button("Calculate Dilution"):
        if c1 == 0 or v1 == 0 or c2 == 0 or v2 == 0:
            st.error("Values cannot be zero!")
        elif c1 and v1 and c2 and v2:
            st.warning("All parameters provided - nothing to calculate!")
        elif not c2:
            c2 = c1 * v1 / v2
            st.success(f"Final concentration (C2): {c2:.4g} {unit_c}")
        elif not v1:
            v1 = c2 * v2 / c1
            st.success(f"Initial volume needed (V1): {v1:.4g} {unit_v}")
        elif not v2:
            v2 = c1 * v1 / c2
            st.success(f"Final volume (V2): {v2:.4g} {unit_v}")
        
        # Display dilution factor
        if c1 and c2:
            dilution_factor = c1 / c2
            st.info(f"Dilution factor: 1:{dilution_factor:.2f}")
            
            # Generate simple plot
            fig, ax = plt.subplots()
            concentrations = [c1, c2]
            volumes = [v1, v2] if v1 and v2 else [1, dilution_factor]
            labels = ['Stock', 'Diluted']
            
            if v1 and v2:
                ax.bar(labels, volumes, color=['blue', 'lightblue'])
                ax.set_ylabel(f"Volume ({unit_v})")
                ax.set_title("Volume Comparison")
            else:
                ax.bar(labels, concentrations, color=['blue', 'lightblue'])
                ax.set_ylabel(f"Concentration ({unit_c})")
                ax.set_title("Concentration Comparison")
            
            st.pyplot(fig)

# ===== TAB 2: SOLUTION PREPARATION =====
with tab2:
    st.header("Solution Preparation")
    
    method = st.radio("Preparation Method", 
                     ["From solid", "From stock solution", "By dilution"],
                     key="prep_method_radio")
    
    if method == "From solid":
        col1, col2 = st.columns(2)
        with col1:
            mw = st.number_input("Molecular weight (g/mol)", min_value=0.0, value=58.44, key="mw_input")
            target_conc = st.number_input("Target concentration", min_value=0.0, value=1.0, key="target_conc_input")
            target_vol = st.number_input("Target volume", min_value=0.0, value=1.0, key="target_vol_input")
            conc_unit = st.selectbox("Concentration unit", ["M", "mM", "µM"], key="solid_conc_unit")
            vol_unit = st.selectbox("Volume unit", ["L", "mL"], key="solid_vol_unit")
        
        with col2:
            if st.button("Calculate amount needed", key="calc_solid_button"):
                if mw and target_conc and target_vol:
                    # Convert units to M and L
                    if conc_unit == "mM":
                        target_conc *= 1e-3
                    elif conc_unit == "µM":
                        target_conc *= 1e-6
                    
                    if vol_unit == "mL":
                        target_vol *= 1e-3
                    
                    mass = target_conc * target_vol * mw
                    st.success(f"Amount needed: {mass:.4g} grams")
                    
                    # Generate plot
                    fig, ax = plt.subplots()
                    ax.pie([mass, target_vol*1000], 
                          labels=[f"Mass: {mass:.2f}g", f"Volume: {target_vol*1000:.1f}mL"],
                          colors=['#ff9999','#66b3ff'],
                          autopct='%1.1f%%')
                    ax.set_title("Mass vs Volume Ratio")
                    st.pyplot(fig)
                else:
                    st.error("Please fill all required fields")
    
    elif method == "From stock solution":
        col1, col2 = st.columns(2)
        with col1:
            stock_conc = st.number_input("Stock concentration", min_value=0.0, value=10.0, key="stock_conc_input")
            stock_unit = st.selectbox("Stock unit", conc_units, key="stock_unit_select")
            target_conc = st.number_input("Target concentration", min_value=0.0, value=1.0, key="target_conc_input_stock")
            target_unit = st.selectbox("Target unit", conc_units, key="target_unit_select")
            target_vol = st.number_input("Target volume", min_value=0.0, value=100.0, key="target_vol_input_stock")
            vol_unit = st.selectbox("Volume unit", vol_units, key="vol_unit_select_stock")
        
        with col2:
            if st.button("Calculate volume to use", key="calc_stock_button"):
                if stock_conc and target_conc and target_vol:
                    # Convert both concentrations to same unit (M)
                    stock_conc_m = stock_conc
                    if stock_unit == "mM":
                        stock_conc_m *= 1e-3
                    elif stock_unit == "µM":
                        stock_conc_m *= 1e-6
                    elif stock_unit == "nM":
                        stock_conc_m *= 1e-9
                    elif stock_unit == "g/L":
                        # Assuming MW is needed for this conversion
                        st.warning("For g/L to M conversion, molecular weight is needed")
                    elif stock_unit == "mg/mL":
                        st.warning("For mg/mL to M conversion, molecular weight is needed")
                    elif stock_unit == "%":
                        st.warning("Percentage calculations assume weight/volume %")
                        stock_conc_m = stock_conc * 10  # Approximation for many solutions
                    
                    target_conc_m = target_conc
                    if target_unit == "mM":
                        target_conc_m *= 1e-3
                    elif target_unit == "µM":
                        target_conc_m *= 1e-6
                    elif target_unit == "nM":
                        target_conc_m *= 1e-9
                    elif target_unit in ["g/L", "mg/mL", "%"]:
                        st.warning("Unit conversion may require molecular weight")
                    
                    if vol_unit == "mL":
                        target_vol_l = target_vol * 1e-3
                    elif vol_unit == "µL":
                        target_vol_l = target_vol * 1e-6
                    else:
                        target_vol_l = target_vol
                    
                    vol_needed = (target_conc_m * target_vol_l) / stock_conc_m
                    st.success(f"Volume of stock needed: {vol_needed*1e3:.4g} mL")
                    
                    # Generate plot
                    fig, ax = plt.subplots()
                    components = ['Stock Solution', 'Diluent']
                    amounts = [vol_needed*1000, (target_vol_l*1000 - vol_needed*1000)]
                    ax.bar(components, amounts, color=['#ff9999','#66b3ff'])
                    ax.set_ylabel("Volume (mL)")
                    ax.set_title("Solution Composition")
                    st.pyplot(fig)
                else:
                    st.error("Please fill all required fields")
    
    elif method == "By dilution":
        st.info("Use the Dilution Calculator in the first tab for this functionality")

# ===== TAB 3: BUFFER CALCULATOR =====
with tab3:
    st.header("Buffer Preparation")
    
    buffer_type = st.selectbox("Select Buffer Type", buffer_types)
    
    if buffer_type == "Tris-HCl":
        st.subheader("Tris-HCl Buffer Calculator")
        col1, col2 = st.columns(2)
        with col1:
            ph = st.slider("Desired pH", 7.0, 9.0, 8.0, 0.1)
            conc = st.number_input("Buffer concentration (M)", 0.01, 1.0, 0.1)
            volume = st.number_input("Final volume (L)", 0.1, 10.0, 1.0)
        with col2:
            st.info(f"""
            **Components needed for {volume} L of {conc} M Tris-HCl (pH {ph}):**
            - Tris base: {conc * volume * 121.14:.2f} g
            - HCl (conc. ~1M): ~{(0.1 * volume * 1000):.1f} mL (adjust for pH)
            - Add HCl dropwise while measuring pH
            """)
    
    elif buffer_type == "PBS":
        st.subheader("PBS Buffer Calculator")
        col1, col2 = st.columns(2)
        with col1:
            conc = st.selectbox("PBS concentration", ["1X", "10X", "0.1X"])
            volume = st.number_input("Final volume (L)", 0.1, 10.0, 1.0)
        with col2:
            st.info(f"""
            **Components needed for {volume} L of {conc} PBS:**
            - NaCl: {8.0 * volume if conc == "1X" else 80.0 * volume if conc == "10X" else 0.8 * volume:.2f} g
            - KCl: {0.2 * volume if conc == "1X" else 2.0 * volume if conc == "10X" else 0.02 * volume:.2f} g
            - Na₂HPO₄: {1.44 * volume if conc == "1X" else 14.4 * volume if conc == "10X" else 0.144 * volume:.2f} g
            - KH₂PO₄: {0.24 * volume if conc == "1X" else 2.4 * volume if conc == "10X" else 0.024 * volume:.2f} g
            - Adjust pH to 7.4
            """)
    
    elif buffer_type == "TAE":
        st.subheader("TAE Buffer Calculator")
        col1, col2 = st.columns(2)
        with col1:
            conc = st.selectbox("TAE concentration", ["1X", "50X"])
            volume = st.number_input("Final volume (L)", 0.1, 10.0, 1.0)
        with col2:
            st.info(f"""
            **Components needed for {volume} L of {conc} TAE:**
            - Tris base: {24.2 * volume if conc == "1X" else 121.0 * volume:.2f} g
            - Acetic acid (glacial): {5.71 * volume if conc == "1X" else 28.55 * volume:.2f} mL
            - 0.5 M EDTA: {4.0 * volume if conc == "1X" else 20.0 * volume:.2f} mL
            """)
    
    elif buffer_type == "Custom":
        st.subheader("Custom Buffer Calculator")
        components = st.text_area("Enter components (one per line)", "Component1, MW, grams\nComponent2, MW, grams")
        if st.button("Calculate Custom Buffer"):
            st.success("Custom buffer calculation will be displayed here.")

# ===== TAB 4: DAILY LAB PLANNER =====
with tab4:
    st.header("Daily Lab Planner")
    
    today = date.today()
    selected_date = st.date_input("Select Date", today)
    
    with st.form("task_form"):
        task = st.text_input("Task Description")
        priority = st.selectbox("Priority", priority_levels)
        status = st.selectbox("Status", ["Not Started", "In Progress", "Completed"])
        
        submitted = st.form_submit_button("Add Task")
        if submitted:
            new_task = pd.DataFrame([[selected_date, task, priority, status]], 
                                  columns=['Date', 'Task', 'Priority', 'Status'])
            st.session_state.daily_tasks = pd.concat([st.session_state.daily_tasks, new_task], ignore_index=True)
            st.success("Task added!")
    
    st.subheader(f"Tasks for {selected_date.strftime('%Y-%m-%d')}")
    
    # Filter tasks for selected date
    daily_tasks = st.session_state.daily_tasks[
        st.session_state.daily_tasks['Date'] == pd.to_datetime(selected_date)
    ]
    
    if not daily_tasks.empty:
        # Sort by priority
        priority_order = {"High": 1, "Medium": 2, "Low": 3}
        daily_tasks['Priority_num'] = daily_tasks['Priority'].map(priority_order)
        daily_tasks = daily_tasks.sort_values('Priority_num').drop('Priority_num', axis=1)
        
        # Display tasks
        for idx, row in daily_tasks.iterrows():
            with st.expander(f"{row['Task']} - {row['Priority']} Priority"):
                st.write(f"**Status**: {row['Status']}")
                if st.button(f"Delete Task {idx+1}", key=f"del_task_{idx}"):
                    st.session_state.daily_tasks = st.session_state.daily_tasks.drop(index=idx)
                    st.rerun()
    else:
        st.info("No tasks scheduled for this date.")
    
    # Progress visualization
    if not daily_tasks.empty:
        st.subheader("Task Progress")
        fig, ax = plt.subplots()
        status_counts = daily_tasks['Status'].value_counts()
        ax.pie(status_counts, labels=status_counts.index, autopct='%1.1f%%', 
               colors=['#ff9999','#66b3ff','#99ff99'])
        ax.set_title("Task Completion Status")
        st.pyplot(fig)

# ===== TAB 5: EXPERIMENT LOG =====
with tab5:
    st.header("Experiment Log")
    
    with st.form("experiment_form"):
        exp_name = st.text_input("Experiment Name")
        exp_date = st.date_input("Date")
        component = st.text_input("Component/Reagent")
        concentration = st.number_input("Concentration", min_value=0.0)
        conc_unit = st.selectbox("Unit", conc_units)
        volume = st.number_input("Volume", min_value=0.0)
        vol_unit = st.selectbox("Volume Unit", vol_units)
        notes = st.text_area("Notes")
        
        submitted = st.form_submit_button("Add to Experiment Log")
        if submitted:
            new_entry = pd.DataFrame([{
                'Experiment': exp_name,
                'Date': exp_date.strftime("%Y-%m-%d"),
                'Component': component,
                'Concentration': f"{concentration} {conc_unit}",
                'Volume': f"{volume} {vol_unit}",
                'Notes': notes
            }])
            
            st.session_state.experiment_data = pd.concat(
                [st.session_state.experiment_data, new_entry], 
                ignore_index=True
            )
            st.success("Entry added to experiment log!")
    
    st.subheader("Current Experiment Data")
    st.dataframe(st.session_state.experiment_data)

# ===== TAB 6: PROTOCOL GENERATOR =====
with tab6:
    st.header("Protocol Generator")
    
    # Protocol metadata
    with st.expander("Protocol Metadata"):
        protocol_title = st.text_input("Protocol Title", "Standard Operating Procedure")
        protocol_author = st.text_input("Author", "Lab Researcher")
        protocol_date = st.date_input("Date", datetime.today())
        protocol_version = st.text_input("Version", "1.0")
        protocol_description = st.text_area("Brief Description")
    
    # Protocol steps management
    st.subheader("Protocol Steps")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        step_type = st.selectbox("Step Type", [
            "Preparation", 
            "Incubation", 
            "Centrifugation", 
            "Measurement",
            "Mixing",
            "Quality Check",
            "Custom"
        ])
    
    with col2:
        step_duration = st.text_input("Duration (optional)", placeholder="e.g., 30 min")
    
    step_description = st.text_area("Step Description", placeholder="Detailed instructions...")
    step_notes = st.text_input("Notes (optional)", placeholder="Special considerations")
    
    col_add, col_clear = st.columns(2)
    with col_add:
        if st.button("Add Step"):
            if step_description:
                new_step = {
                    "type": step_type,
                    "description": step_description,
                    "duration": step_duration,
                    "notes": step_notes,
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M")
                }
                st.session_state.protocol_steps.append(new_step)
                st.success("Step added!")
            else:
                st.warning("Please enter a step description")
    
    with col_clear:
        if st.button("Clear All Steps"):
            st.session_state.protocol_steps = []
            st.success("Protocol steps cleared")
    
    # Display current protocol steps
    st.subheader("Current Protocol Steps")
    if st.session_state.protocol_steps:
        for i, step in enumerate(st.session_state.protocol_steps, 1):
            with st.expander(f"Step {i}: {step['type']}"):
                st.write(f"**Description**: {step['description']}")
                if step['duration']:
                    st.write(f"**Duration**: {step['duration']}")
                if step['notes']:
                    st.write(f"**Notes**: {step['notes']}")
                st.caption(f"Added: {step['timestamp']}")
                
                # Add delete button for each step
                if st.button(f"Delete Step {i}", key=f"del_{i}"):
                    st.session_state.protocol_steps.pop(i-1)
                    st.rerun()
    else:
        st.info("No steps added yet. Add steps to build your protocol.")
    
    # Protocol export options
    st.subheader("Protocol Export")
    
    if st.session_state.protocol_steps:
        export_format = st.selectbox("Export Protocol As", 
                                   ["Markdown", "PDF", "Text", "HTML"])
        
        if export_format == "Markdown":
            # Generate Markdown content
            md_content = f"# {protocol_title}\n\n"
            md_content += f"**Author**: {protocol_author}  \n"
            md_content += f"**Date**: {protocol_date}  \n"
            md_content += f"**Version**: {protocol_version}  \n\n"
            md_content += f"## Description\n{protocol_description}\n\n"
            md_content += "## Protocol Steps\n\n"
            
            for i, step in enumerate(st.session_state.protocol_steps, 1):
                md_content += f"### Step {i}: {step['type']}\n"
                md_content += f"{step['description']}\n\n"
                if step['duration']:
                    md_content += f"- **Duration**: {step['duration']}\n"
                if step['notes']:
                    md_content += f"- **Notes**: {step['notes']}\n"
                md_content += "\n"
            
            st.download_button(
                "Download Markdown",
                data=md_content,
                file_name=f"{protocol_title.replace(' ', '_')}_protocol.md",
                mime="text/markdown"
            )
            
            if st.button("Preview Markdown"):
                st.markdown(md_content)
        
        elif export_format == "PDF":
            st.warning("PDF export requires additional packages. Please use Markdown export and convert to PDF.")
        
        elif export_format == "Text":
            # Generate plain text content
            text_content = f"{protocol_title}\n\n"
            text_content += f"Author: {protocol_author}\n"
            text_content += f"Date: {protocol_date}\n"
            text_content += f"Version: {protocol_version}\n\n"
            text_content += f"Description:\n{protocol_description}\n\n"
            text_content += "Protocol Steps:\n\n"
            
            for i, step in enumerate(st.session_state.protocol_steps, 1):
                text_content += f"Step {i}: {step['type']}\n"
                text_content += f"{step['description']}\n"
                if step['duration']:
                    text_content += f"Duration: {step['duration']}\n"
                if step['notes']:
                    text_content += f"Notes: {step['notes']}\n"
                text_content += "\n"
            
            st.download_button(
                "Download Text",
                data=text_content,
                file_name=f"{protocol_title.replace(' ', '_')}_protocol.txt",
                mime="text/plain"
            )
        
        elif export_format == "HTML":
            # Generate HTML content
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>{protocol_title}</title>
                <style>
                    body {{ font-family: Arial, sans-serif; line-height: 1.6; max-width: 800px; margin: auto; padding: 20px; }}
                    h1 {{ color: #2c3e50; border-bottom: 2px solid #3498db; }}
                    h2 {{ color: #2980b9; }}
                    h3 {{ color: #16a085; }}
                    .meta {{ margin-bottom: 20px; }}
                    .step {{ margin-bottom: 15px; padding: 10px; background-color: #f8f9fa; border-left: 4px solid #3498db; }}
                </style>
            </head>
            <body>
                <h1>{protocol_title}</h1>
                <div class="meta">
                    <p><strong>Author:</strong> {protocol_author}</p>
                    <p><strong>Date:</strong> {protocol_date}</p>
                    <p><strong>Version:</strong> {protocol_version}</p>
                </div>
                <h2>Description</h2>
                <p>{protocol_description}</p>
                <h2>Protocol Steps</h2>
            """
            
            for i, step in enumerate(st.session_state.protocol_steps, 1):
                html_content += f"""
                <div class="step">
                    <h3>Step {i}: {step['type']}</h3>
                    <p>{step['description']}</p>
                """
                if step['duration']:
                    html_content += f"<p><strong>Duration:</strong> {step['duration']}</p>"
                if step['notes']:
                    html_content += f"<p><strong>Notes:</strong> {step['notes']}</p>"
                html_content += "</div>"
            
            html_content += "</body></html>"
            
            st.download_button(
                "Download HTML",
                data=html_content,
                file_name=f"{protocol_title.replace(' ', '_')}_protocol.html",
                mime="text/html"
            )
            
            if st.button("Preview HTML"):
                st.components.v1.html(html_content, height=600, scrolling=True)
    else:
        st.warning("No protocol steps to export. Add steps first.")

# ===== TAB 7: DATA VISUALIZATION =====
with tab7:
    st.header("Data Visualization")
    
    st.subheader("Add Data for Plotting")
    col1, col2 = st.columns(2)
    with col1:
        x_val = st.number_input("X value", value=0.0)
        y_val = st.number_input("Y value", value=0.0)
        series_name = st.text_input("Series name", "Series 1")
    
    with col2:
        if st.button("Add Data Point"):
            new_point = pd.DataFrame([[x_val, y_val, series_name]], 
                                   columns=['x', 'y', 'series'])
            st.session_state.plot_data = pd.concat([st.session_state.plot_data, new_point], 
                                                ignore_index=True)
            st.success("Data point added!")
        
        if st.button("Clear All Data"):
            st.session_state.plot_data = pd.DataFrame(columns=['x', 'y', 'series'])
            st.success("Plot data cleared!")
    
    st.subheader("Current Plot Data")
    st.dataframe(st.session_state.plot_data)
    
    st.subheader("Configure Plot")
    plot_type = st.selectbox("Plot Type", 
                            ["Line Plot", "Scatter Plot", "Bar Plot", "Pie Chart"])
    
    if not st.session_state.plot_data.empty:
        fig, ax = plt.subplots()
        
        if plot_type in ["Line Plot", "Scatter Plot"]:
            for series in st.session_state.plot_data['series'].unique():
                series_data = st.session_state.plot_data[st.session_state.plot_data['series'] == series]
                if plot_type == "Line Plot":
                    ax.plot(series_data['x'], series_data['y'], 'o-', label=series)
                else:
                    ax.scatter(series_data['x'], series_data['y'], label=series)
            
            ax.set_xlabel("X Axis")
            ax.set_ylabel("Y Axis")
            ax.legend()
            ax.grid(True)
        
        elif plot_type == "Bar Plot":
            series_data = st.session_state.plot_data.groupby('series')['y'].mean()
            ax.bar(series_data.index, series_data.values)
            ax.set_ylabel("Y Value")
        
        elif plot_type == "Pie Chart":
            series_data = st.session_state.plot_data.groupby('series')['y'].sum()
            ax.pie(series_data.values, labels=series_data.index, autopct='%1.1f%%')
        
        ax.set_title("Experimental Data Visualization")
        st.pyplot(fig)
        
        # Export plot
        buf = BytesIO()
        plt.savefig(buf, format="png", dpi=300)
        st.download_button(
            "Download Plot as PNG",
            data=buf.getvalue(),
            file_name="lab_plot.png",
            mime="image/png"
        )
    else:
        st.warning("No data available for plotting. Add data points first.")

# ===== TAB 8: DATA EXPORT =====
with tab8:
    st.header("Data Export")
    
    if not st.session_state.experiment_data.empty:
        st.subheader("Experiment Data")
        st.dataframe(st.session_state.experiment_data)
        
        # Export options
        export_format = st.selectbox("Export Format", 
                                   ["CSV", "Excel", "JSON", "Markdown"])
        
        if export_format == "CSV":
            csv = st.session_state.experiment_data.to_csv(index=False)
            st.download_button(
                "Download CSV",
                data=csv,
                file_name="experiment_data.csv",
                mime="text/csv"
            )
        elif export_format == "Excel":
            excel_buffer = StringIO()
            st.session_state.experiment_data.to_excel(excel_buffer, index=False)
            st.download_button(
                "Download Excel",
                data=excel_buffer.getvalue(),
                file_name="experiment_data.xlsx",
                mime="application/vnd.ms-excel"
            )
        elif export_format == "JSON":
            json = st.session_state.experiment_data.to_json(indent=2)
            st.download_button(
                "Download JSON",
                data=json,
                file_name="experiment_data.json",
                mime="application/json"
            )
        elif export_format == "Markdown":
            md = st.session_state.experiment_data.to_markdown(index=False)
            st.download_button(
                "Download Markdown",
                data=md,
                file_name="experiment_data.md",
                mime="text/markdown"
            )
        
        # Print functionality
        if st.button("Print Data"):
            st.write("```python")
            st.write(st.session_state.experiment_data.to_string(index=False))
            st.write("```")
    else:
        st.warning("No experiment data available to export")

# Sidebar with references
st.sidebar.header("Reference Tables")
st.sidebar.subheader("Common Molecular Weights")
mw_data = {
    "Compound": ["NaCl", "Tris", "EDTA", "SDS", "NaOH", "HCl"],
    "MW (g/mol)": [58.44, 121.14, 372.24, 288.38, 40.00, 36.46]
}
st.sidebar.table(pd.DataFrame(mw_data))

st.sidebar.subheader("Common Buffer Recipes")
buffer_recipes = {
    "Buffer": ["Tris-HCl (pH 8.0)", "PBS (1X)", "TAE (1X)"],
    "Composition": ["Tris + HCl", "NaCl + KCl + Phosphates", "Tris + Acetate + EDTA"]
}
st.sidebar.table(pd.DataFrame(buffer_recipes))
