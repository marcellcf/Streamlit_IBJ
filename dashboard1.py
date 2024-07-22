import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from wordcloud import WordCloud
import matplotlib.pyplot as plt

# Set page config at the very beginning
st.set_page_config(page_title="Iramanesia Dashboard", page_icon="🎵", layout="wide")

# Load data
@st.cache_data
def load_data():
    data = pd.read_csv('Data.csv')
    data = data.drop(index=data.index[175:])
    data['Name'] = data['Name'].astype(str)
    data['Total Streams'] = data[['Spotify Streams', 'YouTube Music Plays', 'Joox Streams', 'Apple Music Streams']].sum(axis=1)
    data['SD'] = data[['Spotify Streams', 'YouTube Music Plays', 'Joox Streams', 'Apple Music Streams']].std(axis=1)
    return data

data = load_data()

# Streamlit layout
st.title('Iramanesia Content Performance Analysis')

# Sidebar for navigation
st.sidebar.title("Navigation")
options = st.sidebar.radio("Select an option", ["Home", "Top Artists", "Platform Comparison", "Artist Comparison", "Data Explorer"])

# Custom theme
custom_theme = {
    'plot_bgcolor': 'rgba(0, 0, 0, 0)',
    'paper_bgcolor': 'rgba(0, 0, 0, 0)',
    'title_font_color': '#FFFFFF',
    'font_color': '#FFFFFF',
    'font_family': 'Arial'
}

# Home page
# Home page
if options == "Home":
    st.header("Selamat Datang di Dashboard Analisis Performa Konten Iramanesia!")
    # Word cloud of artists
    st.subheader("Word Cloud Artis")
    st.write("Ukuran nama artis menunjukkan jumlah total streams-nya.")
    wordcloud = WordCloud(width=800, height=400, background_color='white').generate_from_frequencies(
        dict(zip(data['Name'], data['Total Streams']))
    )
    fig, ax = plt.subplots()
    ax.imshow(wordcloud, interpolation='bilinear')
    ax.axis('off')
    st.pyplot(fig)
    st.write("""
    Dashboard ini menyajikan wawasan tentang performa berbagai artis di berbagai platform streaming.
    Gunakan panel navigasi di sebelah kiri untuk menjelajahi analisis yang berbeda.
    
    Berikut adalah penjelasan tentang menu navigasi yang tersedia:
    
    1. **Home**: Halaman ini, yang memberikan gambaran umum dashboard dan penjelasan navigasi.
    
    2. **Top Artists**: Menampilkan analisis artis teratas berdasarkan:
       - Total Streams: Melihat artis dengan jumlah stream terbanyak secara keseluruhan.
       - Konsistensi: Menemukan artis dengan performa yang paling konsisten di semua platform.
       - Per Platform: Melihat artis teratas untuk setiap platform streaming.
    
    3. **Platform Comparison**: Membandingkan performa antar platform streaming, termasuk:
       - Grafik perbandingan artis teratas di setiap platform.
       - Peta panas korelasi antar platform.
       - Diagram pie distribusi keseluruhan stream di semua platform.
    
    4. **Artist Comparison**: Membandingkan performa artis secara langsung, dengan fitur:
       - Pencarian dan pemilihan multiple artis.
       - Grafik batang perbandingan stream per platform untuk artis yang dipilih.
       - Diagram pie distribusi stream untuk setiap artis yang dipilih.
    
    5. **Data Explorer**: Menjelajahi data mentah dan statistik, termasuk:
       - Plot scatter interaktif dengan sumbu yang bisa dipilih.
       - Tabel data mentah dengan fungsi pencarian.
       - Opsi untuk mengunduh data.
       - Statistik ringkasan dan matriks korelasi.
    
    Selamat menjelajahi data!
    """)

    

# Top Artists page
elif options == "Top Artists":
    st.header("Top Artists Analysis")

    tab1, tab2, tab3 = st.tabs(["By Total Streams", "Most Consistent", "By Platform"])

    with tab1:
        st.subheader("Top Artists by Total Streams")
        top_n = st.slider("Select number of top artists", 5, 20, 10, key="total_streams_slider")
        top_artists = data.nlargest(top_n, 'Total Streams')
        
        fig = px.bar(top_artists, x='Total Streams', y='Name', orientation='h', 
                     title=f'Top {top_n} Artists by Total Streams', template='plotly_dark', 
                     color='Total Streams', color_continuous_scale='Viridis')
        fig.update_layout(yaxis={'categoryorder':'total ascending'}, **custom_theme)
        st.plotly_chart(fig, use_container_width=True)

    with tab2:
        st.subheader("Most Consistent Artists (Lowest Standard Deviation)")
        top_n = st.slider("Select number of consistent artists", 5, 20, 5, key="consistent_artists_slider")
        top_consistent_artists = data.nsmallest(top_n, 'SD')
        
        fig = px.bar(top_consistent_artists, x='SD', y='Name', orientation='h', 
                     title=f'Top {top_n} Artists with Highest Consistency', template='plotly_dark', 
                     color='SD', color_continuous_scale='Blues')
        fig.update_layout(yaxis={'categoryorder':'total ascending'}, **custom_theme)
        st.plotly_chart(fig, use_container_width=True)

    with tab3:
        st.subheader("Top Artists by Platform")
        platform = st.selectbox("Select a platform", ['Spotify Streams', 'YouTube Music Plays', 'Joox Streams', 'Apple Music Streams'])
        top_n = st.slider("Number of top artists to show", 5, 20, 10, key="platform_top_artists_slider")

        top_artists = data.nlargest(top_n, platform)
        fig = px.bar(top_artists, x='Name', y=platform, title=f"Top {top_n} Artists on {platform}")
        fig.update_layout(**custom_theme)
        st.plotly_chart(fig, use_container_width=True)

# Platform Comparison page
elif options == "Platform Comparison":
    st.header("Platform Comparison")

    platforms = ['Spotify Streams', 'YouTube Music Plays', 'Joox Streams', 'Apple Music Streams']
    selected_platforms = st.multiselect("Select platforms to compare", platforms, default=platforms)

    top_n = st.slider("Select number of top artists per platform", 1, 4, 3)

    fig = go.Figure()
    for platform in selected_platforms:
        top_artists = data.nlargest(top_n, platform)
        fig.add_trace(go.Bar(
            x=top_artists[platform],
            y=top_artists['Name'],
            name=platform,
            orientation='h'
        ))
        
    fig.update_layout(barmode='group', title=f'Top {top_n} Artists by Platform Streams', 
                      template='plotly_dark', **custom_theme)
    fig.update_yaxes(categoryorder='total ascending')
    st.plotly_chart(fig, use_container_width=True)

    # Correlation heatmap
    st.subheader("Platform Correlation Heatmap")
    corr = data[selected_platforms].corr()
    fig = px.imshow(corr, text_auto=True, aspect="auto", title="Correlation between Platforms")
    st.plotly_chart(fig, use_container_width=True)

    # Platform Distribution Pie Chart
    st.subheader("Overall Platform Distribution")
    platform_totals = data[platforms].sum()
    fig = px.pie(values=platform_totals.values, names=platform_totals.index, 
                 title="Overall Distribution of Streams Across Platforms")
    st.plotly_chart(fig, use_container_width=True)

# Artist Comparison page
elif options == "Artist Comparison":
    st.header("Compare Artists Across Platforms")

    search_term = st.text_input("Search for an artist")
    filtered_artists = data[data['Name'].str.contains(search_term, case=False, na=False)]
    
    selected_artists = st.multiselect("Select Artists to Compare", filtered_artists['Name'].unique())
    
    if selected_artists:
        artists_data = data[data['Name'].isin(selected_artists)]
        platforms = ['Spotify Streams', 'YouTube Music Plays', 'Joox Streams', 'Apple Music Streams']
        
        fig = go.Figure()
        for artist in selected_artists:
            artist_data = artists_data[artists_data['Name'] == artist]
            fig.add_trace(go.Bar(
                x=platforms,
                y=artist_data[platforms].values[0],
                name=artist
            ))
        
        fig.update_layout(title='Streams per Platform for Selected Artists', 
                          template='plotly_dark', **custom_theme,
                          barmode='group')
        
        st.plotly_chart(fig, use_container_width=True)

        # Pie charts for individual artists
        cols = st.columns(len(selected_artists))
        for i, artist in enumerate(selected_artists):
            with cols[i]:
                artist_data = artists_data[artists_data['Name'] == artist]
                fig = px.pie(values=artist_data[platforms].values[0], names=platforms, 
                             title=f"Stream Distribution for {artist}")
                st.plotly_chart(fig, use_container_width=True)

# Data Explorer page
elif options == "Data Explorer":
    st.header("Data Explorer")

    # Allow users to select x and y axes for scatter plot
    x_axis = st.selectbox("Choose x-axis", ['Spotify Streams', 'YouTube Music Plays', 'Joox Streams', 'Apple Music Streams', 'Total Streams'])
    y_axis = st.selectbox("Choose y-axis", ['Spotify Streams', 'YouTube Music Plays', 'Joox Streams', 'Apple Music Streams', 'Total Streams'])

    fig = px.scatter(data, x=x_axis, y=y_axis, hover_name='Name', color='Total Streams',
                     title=f'{x_axis} vs {y_axis}', template='plotly_dark')
    fig.update_layout(**custom_theme)
    st.plotly_chart(fig, use_container_width=True)

    # Data table with search functionality
    st.subheader("Raw Data")
    search = st.text_input("Search artists")
    filtered_data = data[data['Name'].str.contains(search, case=False, na=False)]
    st.dataframe(filtered_data)

    # Download button
    if st.button('Download Data as CSV'):
        csv = filtered_data.to_csv(index=False)
        st.download_button(label="Download data as CSV", 
                           data=csv, 
                           file_name="iramanesia_data.csv", 
                           mime="text/csv")

    # Summary statistics
    st.subheader("Summary Statistics")
    st.write(data[['Spotify Streams', 'YouTube Music Plays', 'Joox Streams', 'Apple Music Streams', 'Total Streams']].describe())

    # Correlation matrix
    st.subheader("Correlation Matrix")
    corr_matrix = data[['Spotify Streams', 'YouTube Music Plays', 'Joox Streams', 'Apple Music Streams', 'Total Streams']].corr()
    fig = px.imshow(corr_matrix, text_auto=True, aspect="auto")
    st.plotly_chart(fig, use_container_width=True)