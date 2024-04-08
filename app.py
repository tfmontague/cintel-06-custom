#-----------------------------------------------------------------------------
# imports (at the top)
#-----------------------------------------------------------------------------
import plotly.express as px
from shiny.express import input, ui
from shinywidgets import render_plotly, render_widget
from shinyswatch import theme
from palmerpenguins import load_penguins
import palmerpenguins
import seaborn as sns
from shiny import reactive, render
from faicons import icon_svg
import json
import pathlib
from ipyleaflet import Map, Marker

#-----------------------------------------------------------------------------
# define a reactive calc to filter the palmer penguins dataset
#-----------------------------------------------------------------------------
penguins_df = palmerpenguins.load_penguins()

@reactive.calc
def filtered_data():
    selected_species = input.selected_species_list()
    selected_islands = input.selected_island_list()
    mass_filter = input.mass_filter()
    filtered_df = penguins_df[
        (penguins_df['species'].isin(selected_species)) &
        (penguins_df['island'].isin(selected_islands)) &
        (penguins_df['body_mass_g'] <= mass_filter)
    ]    
    return filtered_df


#-----------------------------------------------------------------------------
# The overall page options
#-----------------------------------------------------------------------------
# Name the page
ui.page_opts(title="TFMONTAGUE's Customized Penguin Dashboard", fillable=True)

# Add a color theme to the dashboard
theme.quartz()


#-----------------------------------------------------------------------------
# A sidebar
#-----------------------------------------------------------------------------
with ui.sidebar(open="open"):  
    ui.HTML('<h3 style="font-size: medium;">Dashboard Configuration Options</h3>')
    with ui.accordion():
        with ui.accordion_panel("Attribute Selection"):
            ui.input_selectize("selected_attribute", "Select an attribute:", 
                          ["bill_length_mm", "bill_depth_mm", "flipper_length_mm", "body_mass_g"])
        with ui.accordion_panel("Histogram Bins Configuration"):
            ui.input_numeric("plotly_bin_count", "# of Histogram Bins:", value=20, min=1, max=100)
        with ui.accordion_panel("Seaborn Bins Slider"):
            ui.input_slider("seaborn_bin_count", "# of Seaborn Bins:", min=1, max=50, value=10)
        with ui.accordion_panel("Species Filter"):
            ui.input_checkbox_group("selected_species_list", "Filter by Species:", 
                                choices=["Adelie", "Gentoo", "Chinstrap"], 
                                selected=["Adelie"], inline=True)
        with ui.accordion_panel("Island Filter"):
            ui.input_checkbox_group("selected_island_list", "Filter by Island:", 
                                choices=["Torgersen", "Biscoe", "Dream"], 
                                selected=["Torgersen", "Biscoe", "Dream"], inline=True)
        with ui.accordion_panel("Mass Filter"):
            ui.input_slider("mass_filter", "Mass (g)", 2000, 6000, 6000)
    
    ui.hr()

    @render.ui
    def selected_info2():
        selected_attribute = input.selected_attribute()
        plotly_bin_count = input.plotly_bin_count()
        seaborn_bin_count = input.seaborn_bin_count()
        selected_species = input.selected_species_list()
        selected_species_str = ", ".join(selected_species)
        selected_island = input.selected_island_list()
        selected_island_str = ", ".join(selected_island)
        mass_filter = input.mass_filter()
    
        info_html = f"""
        <div style="font-size: 100%; line-height: 1;">
            <h6 style="margin-bottom: 0;">Selected Configuration:</h6>
            <p style="margin-top: 1; margin-bottom: 1;"><strong>Selected attribute:</strong> {selected_attribute}</p>
            <p style="margin-top: 1; margin-bottom: 1;"><strong>Plotly bin count:</strong> {plotly_bin_count}</p>
            <p style="margin-top: 1; margin-bottom: 1;"><strong>Seaborn bin count:</strong> {seaborn_bin_count}</p>
            <p style="margin-top: 1; margin-bottom: 1;"><strong>Selected species:</strong> {selected_species_str}</p>
            <p style="margin-top: 1; margin-bottom: 1;"><strong>Selected islands:</strong> {selected_island_str}</p>
            <p style="margin-top: 1; margin-bottom: 1;"><strong>Maximum body mass (g):</strong> {mass_filter}</p>
        </div>
        """
        return ui.HTML(info_html)

    ui.hr()
    ui.a("Repository for Continuous Intelligence Project 6 - Custom Interactive App", href="https://github.com/tfmontague/cintel-06-custom", target="_blank")


#-----------------------------------------------------------------------------
# The main section with ui cards, value boxes, and space for grids and charts
#-----------------------------------------------------------------------------
with ui.accordion():
    with ui.accordion_panel("Dashboard Overview"):
        with ui.layout_columns():
            with ui.value_box(showcase=icon_svg("earlybirds"), max_height="300px"):
                "Total Penguins Filtered"
                @render.text
                def display_penguin_count():
                    df = filtered_data()
                    return f"{len(df)} penguins"

            with ui.value_box(showcase=icon_svg("ruler-horizontal"), max_height="300px", theme="bg-gradient-green"):
                "Average Bill Length"
                @render.text
                def average_bill_length():
                    df = filtered_data()
                    return f"{df['bill_length_mm'].mean():.2f} mm" if not df.empty else "N/A"

            with ui.value_box(showcase=icon_svg("ruler-vertical"), max_height="300px", theme="bg-gradient-orange"):
                "Average Bill Depth"
                @render.text
                def average_bill_depth():
                    df = filtered_data()
                    return f"{df['bill_depth_mm'].mean():.2f} mm" if not df.empty else "N/A"
                

# Accordion component for the histograms
    with ui.accordion_panel("Histograms"):
            with ui.card():
                ui.card_header("Plotly Histogram: All Species")
                @render_plotly
                def plotly_histogram():
                    return px.histogram(
                        filtered_data(),
                        x=input.selected_attribute(),
                        nbins=input.plotly_bin_count(),
                        color="species",
                    )
                
            with ui.card():
                ui.card_header("Seaborn Histogram: All Species")
                @render.plot
                def seaborn_histogram():
                    ax = sns.histplot(
                        data=filtered_data(),
                        x=input.selected_attribute(),
                        bins=input.seaborn_bin_count()
                    )
                    ax.set_title("Palmer Penguins")
                    ax.set_xlabel(input.selected_attribute())
                    ax.set_ylabel("Count")
                    return ax

    with ui.accordion_panel("Scatterplot"):
        with ui.card():
            ui.card_header("Plotly Scatterplot: Species")
            @render_plotly
            def plotly_scatterplot():
                return px.scatter(filtered_data(),
                                    x="flipper_length_mm",
                                    y="body_mass_g",
                                    color="species",
                                    hover_name="island",
                                    labels={
                                        "flipper_length_mm": "Flipper Length (mm)",
                                        "body_mass_g": "Body Mass (g)",
                                        "species": "Species",
                                        "bill_length_mm": "Bill Length (mm)",
                                        "island": "Island"
                                    },
                                    title="Penguin Species Measurements",
                                    size_max=12
                                )
# New accordion panel for the data table
    with ui.accordion_panel("Data Table"):
        with ui.card(max_height="300px"):
            ui.card_header("Palmer Penguins Data Table")
            @render.data_frame
            def render_penguins_table():
                return filtered_data()

    with ui.accordion_panel("Map"):
        with open(pathlib.Path(__file__).parent / "antartica_110.geo.json", "r") as f:
            island_boundaries = json.load(f)
        with ui.card(height="700px"):
            ui.card_header("Island Locations")
            @render_widget  
            def map():
                map_center = (-64.7, -64)  # Approximate center for the islands
                map_zoom = 8  # Zoom level to show the islands clearly
                
                penguin_map = Map(center=map_center, zoom=map_zoom)
                
                # Add markers for the filtered islands
                for island_name in input.selected_island_list():
                    # Assuming `island_boundaries` contains locations for the islands
                    island_location = island_boundaries.get(island_name)
                    if island_location:
                        marker = Marker(location=(island_location['latitude'], island_location['longitude']), draggable=False)
                        penguin_map.add_layer(marker)
                
                return penguin_map
