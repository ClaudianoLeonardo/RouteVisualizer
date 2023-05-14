import streamlit as st
from routes import finding_routes
from utils import generate_graph, get_location

if 'CTR' not in st.session_state:
    st.session_state['CTR'] = False
if 'STR' not in st.session_state:
    st.session_state['STR'] = False
if 'CTY' not in st.session_state:
    st.session_state['CTY'] = False

def disable(value):
    st.session_state[value] = True

st.markdown("# Route Visualizer :car:")
st.markdown("## Brazil")
st.markdown("### Enter the state you are visiting")
state = st.text_input(label='', label_visibility="collapsed", disabled=st.session_state.STR, key='state',on_change=disable('STR'))
if state:    
    st.markdown("### Enter the city you are visiting")
    city = st.text_input(label='', label_visibility="collapsed", disabled= st.session_state.CTY, key='city',on_change=disable('CTY'))
    if city:
        st.markdown("### Enter points you intend to visit")
        pontos = st.text_input(label='Enter points separated by commas. The first point is the origin and the last point is the final destination.', 
                                    label_visibility="visible", disabled= False, key='ponto')
        if pontos:
            graph = generate_graph(city, state)
            HILLS, START_HILL, END_HILL = get_location(pontos, city, state)       


            mapa, distance = finding_routes(graph, HILLS,START_HILL,END_HILL,pontos,
                                    max_iter=2000,
                                    max_iter_without_improvement=300)
                           
            html = mapa.get_root().render()
            with st.container(): 
                avg_emi_C02 = round(distance*120, 2)
                st.components.v1.html(html, width=800, height=600, scrolling=False)
                st.caption(f'Average amount of CO2 emitted on the route: {avg_emi_C02} g/km ')

                with open('optimal.html') as map:
                    bt = st.download_button(label='Export as html', data =map , file_name='map.html')   
            
