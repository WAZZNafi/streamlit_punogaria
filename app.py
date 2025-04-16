import streamlit as st

st.title("Nafi's Portfolio app")
st.write("Wellcome! This is my first portfolio app using Streamlit")

container = st.container()
with container:
    st.subheader("About me")
    st.write("I am a data scientist with experience in machine learning and data analysis")
    st.write("I am currently working on a project using Streamlit")
    st.area_chart([100, 75, 85, 69, 77])
    prompt = st.chat_input("Ask me anything about my portfolio")
    if prompt:
        st.write("You asked:", prompt)
        st.write("This is a placeholder for the answer to your question.")
        st.write("I will add this feature in the future.")
        st.balloons()
        st.snow()
        st.snow()
        st.snow()
        st.snow()
        st.snow()   

    st.logo("https://www.streamlit.io/images/brand/streamlit-mark-color.png")
    st.image("https://www.streamlit.io/images/brand/streamlit-mark-color.png", caption="Streamlit logo")
    st.video("https://youtu.be/G5V4wBjR880?si=V-_44BYkjpoybAtJ")
    st.audio("https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3", format="audio/mp3")

    st.file_uploader("Upload a file", type=["csv", "txt", "pdf", "png", "jpg"])
    st.download_button("Download", "This is a placeholder for the download button")