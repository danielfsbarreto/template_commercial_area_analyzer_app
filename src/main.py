from uuid import uuid4

import streamlit as st

from services import ExecutionsService
from utils import download_link, relative_time, render_badge, render_table

if "upload_key" not in st.session_state:
    st.session_state["upload_key"] = str(uuid4())


@st.fragment
def execution_fragment(execution_id: str):
    execution = ExecutionsService().find(execution_id)

    with st.expander(f"{execution.uuid}", expanded=False):
        first_column, second_column = st.columns(2)
        with first_column:
            st.markdown(**relative_time("Started at", execution.started_at))  # type: ignore
            st.markdown(f"**Status:** {render_badge(execution)}")
            st.button(
                "",
                icon=":material/refresh:",
                key=f"refresh-button-{execution.uuid}",
                type="secondary",
            )
        with second_column:
            st.markdown(
                **relative_time("Completed at", execution.completed_at)  # type: ignore
            )
        input_tab, output_tab = st.tabs(["Input", "Output"])
        with input_tab:
            st.markdown(
                f"**Download:** {download_link(execution.input_file)}",
                unsafe_allow_html=True,
            )
            st.dataframe(render_table(execution.input_file))
        with output_tab:
            st.markdown(
                f"**Download:** {download_link(execution.output_file)}",
                unsafe_allow_html=True,
            )
            st.dataframe(render_table(execution.output_file))


st.html("""
<style>
    .footer-center {
        display: flex;
        justify-content: center;
        align-items: center;
        text-align: center;
        color: rgb(100, 102, 106);
        font-size: 0.9rem;
    }
</style>
""")

with st.sidebar:
    st.logo("src/public/logo.svg", size="large")
    st.text(
        """
        This demo application showcases how to design effective visual interfaces that integrate seamlessly with CrewAI automations — supporting both crew-based and flow-based processes.

        Explore interactive examples that highlight best practices for building intuitive,productive user experiences powered by CrewAI's automation capabilities.
        """
    )
    st.markdown(
        "[**Sign up for a Free Trial**](https://app.crewai.com/)",
    )

with st._bottom:
    st.html(
        """
            <p class="footer-center">
                CrewAI © Copyright 2025, All Rights Reserved by CrewAI™, Inc.
            </p>
            """
    )

with st.container():
    st.title("Commercial Area Analyzer")
    with st.form("upload_form", clear_on_submit=True, border=False):
        uploader = st.file_uploader(
            "Companies",
            key=st.session_state["upload_key"],
            type="csv",
            help="Upload a CSV file with all companies you want to research",
        )
        st.form_submit_button(
            "Upload",
            type="primary",
        )

    if uploader and uploader.getvalue() is not None:
        companies_csv = uploader.getvalue()
        ExecutionsService().start_execution(companies_csv)
        st.session_state["upload_key"] = str(uuid4())

    for execution_id in ExecutionsService().list_execution_ids():
        execution_fragment(execution_id)
