import streamlit as st

from services import ExecutionsService
from utils import download_link, relative_time, render_badge, render_table

if "executions" not in st.session_state:
    st.session_state.executions = []


@st.fragment
def executions_section():
    st.button("Refresh")
    st.session_state.executions = ExecutionsService().list_executions()

    if not st.session_state.executions:
        st.info("No executions found")
        return

    for execution in st.session_state.executions:
        with st.container(key=execution.uuid):
            with st.expander(f"{execution.uuid}", expanded=False):
                first_column, second_column = st.columns(2)
                with first_column:
                    st.markdown(**relative_time("Started at", execution.started_at))  # type: ignore
                    st.badge(**render_badge(execution))  # type: ignore
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
    st.divider()
    with st.form("upload_form", clear_on_submit=True, border=False):
        st.file_uploader(
            "Companies",
            key="file_uploader",
            type="csv",
            help="Upload a CSV file with all companies you want to research",
        )
        st.form_submit_button(
            "Upload",
            type="primary",
        )

with st.container():
    st.title("Commercial Area Analyzer")
    executions_section()

with st._bottom:
    st.html(
        """
        <p class="footer-center">
            CrewAI © Copyright 2025, All Rights Reserved by CrewAI™, Inc.
        </p>
        """
    )

if st.session_state.file_uploader is not None:
    companies_csv = st.session_state.file_uploader.getvalue()
    ExecutionsService().start_execution(companies_csv)
    st.toast('Execution triggered! Hit "Refresh" to see the results.', icon="🎉")
