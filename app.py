import streamlit as st
import json
import os
import re
import pandas as pd
from researcher import SchoolResearcher
from essay_helper import EssayHelper

# Set page configuration
st.set_page_config(
    page_title="US Transfer Research Assistant",
    page_icon="🎓",
    layout="wide"
)

# Constants
PROFILE_PATH = os.path.join("data", "profile.json")
APPLICATIONS_PATH = os.path.join("data", "applications.json")
RESEARCH_DIR = "research_notes"
ESSAY_DIR = "essays"

# --- Helper Functions ---

def load_profile():
    if os.path.exists(PROFILE_PATH):
        with open(PROFILE_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_profile(profile):
    os.makedirs("data", exist_ok=True)
    with open(PROFILE_PATH, 'w', encoding='utf-8') as f:
        json.dump(profile, f, indent=4)

def load_applications():
    if os.path.exists(APPLICATIONS_PATH):
        with open(APPLICATIONS_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_applications(apps):
    os.makedirs("data", exist_ok=True)
    with open(APPLICATIONS_PATH, 'w', encoding='utf-8') as f:
        json.dump(apps, f, indent=4)


def load_research_data(school_name):
    filename = os.path.join(RESEARCH_DIR, f"{school_name.replace(' ', '_')}.json")
    if os.path.exists(filename):
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)
    return None

def load_essay_outline(school_name):
    filename = os.path.join(ESSAY_DIR, f"{school_name.replace(' ', '_')}_outline.md")
    if os.path.exists(filename):
        with open(filename, 'r', encoding='utf-8') as f:
            return f.read()
    return None

def load_essay_prompts():
    path = os.path.join("data", "essay_prompts.json")
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def load_research_notes():
    path = os.path.join("data", "research_notes.json")
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_research_notes(notes):
    path = os.path.join("data", "research_notes.json")
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(notes, f, indent=4, ensure_ascii=False)

# --- Main App ---

st.sidebar.title("🎓 US Transfer Assistant")

# Sidebar Navigation
page = st.sidebar.radio("Navigation", ["Home", "Profile", "Transfer Majors", "Department Websites", "School Research", "Essay Helper", "Application Tracker"])

# Initialize session state for profile
if 'profile' not in st.session_state:
    st.session_state.profile = load_profile()

profile = st.session_state.profile

# Robust container handling for different Streamlit versions
try:
    # Try using the key parameter (Streamlit 1.35.0+) which handles clearing automatically
    main_container = st.container(key=f"main_content_{page}")
except TypeError:
    # Fallback for older Streamlit versions
    # Use a single empty placeholder and clear it explicitly when page changes
    if "main_placeholder" not in st.session_state:
        st.session_state.main_placeholder = st.empty()
    
    main_container = st.session_state.main_placeholder.container()

with main_container:
    # --- Page: Home ---
    if page == "Home":
        st.title("🎓 US Undergraduate Transfer Research Assistant")
        st.markdown("""
        ### 欢迎使用美本转学调研助手
        **Welcome to the US Transfer Research Assistant!**

        This tool is designed to help you organize and streamline your transfer application process. 
        (本工具旨在帮助你高效管理转学申请的调研过程。)

        请从左侧侧边栏选择功能模块：
        - **Profile (个人档案)**: 设置你的背景信息和目标院校。
        - **School Research (学校调研)**: 针对目标院校进行深度信息挖掘。
        - **Essay Helper (文书助手)**: 基于调研结果生成文书大纲。
        - **Transfer Majors (转学专业)**: 查看目标院校的转学专业列表和录取难度。
        - **Application Tracker (申请进度)**: 记录和管理你的申请进度。
        """)

    # --- Page: Profile ---
    elif page == "Profile":
        st.header("👤 Your Profile (个人档案)")
        st.markdown("""
        **功能说明：**
        在此处完善你的个人背景信息（如当前学校、专业、已修课程、兴趣方向）以及目标转学院校列表。
        这些信息将被用于后续的学校调研和文书生成，确保结果的个性化和针对性。
        """)
        
        with st.form("profile_form"):
            col1, col2 = st.columns(2)
            with col1:
                current_school = st.text_input("Current School", value=profile.get("current_school", ""))
                major = st.text_input("Current Major/Track", value=profile.get("track", ""))
                college = st.text_input("Current College", value=profile.get("college", ""))
                class_of = st.text_input("Class of", value=profile.get("class_of", "2029"))
            
            with col2:
                current_year = st.selectbox("Current Year", ["Freshman", "Sophomore", "Junior"], index=0 if profile.get("current_year") == "Freshman" else 1)
                transfer_term = st.text_input("Transfer Term", value=profile.get("transfer_term", "Fall 2026"))

            st.subheader("Courses")
            col_c1, col_c2 = st.columns(2)
            with col_c1:
                courses_taken_str = st.text_area("Courses Taken (one per line)", value="\n".join(profile.get("courses_taken", [])))
            with col_c2:
                courses_in_progress_str = st.text_area("Courses In Progress (one per line)", value="\n".join(profile.get("courses_in_progress", [])))

            st.subheader("Interests")
            interests_str = st.text_area("Interests (comma separated)", value=", ".join(profile.get("interests", [])))
            
            st.subheader("Target Schools")
            target_schools_str = st.text_area("Target Schools (one per line)", value="\n".join(profile.get("target_schools", [])))

            submitted = st.form_submit_button("Save Profile")
            
            if submitted:
                profile["current_school"] = current_school
                profile["track"] = major
                profile["college"] = college
                profile["class_of"] = class_of
                profile["current_year"] = current_year
                profile["transfer_term"] = transfer_term
                profile["interests"] = [i.strip() for i in interests_str.split(",") if i.strip()]
                profile["courses_taken"] = [c.strip() for c in courses_taken_str.split("\n") if c.strip()]
                profile["courses_in_progress"] = [c.strip() for c in courses_in_progress_str.split("\n") if c.strip()]
                profile["target_schools"] = [s.strip() for s in target_schools_str.split("\n") if s.strip()]
                
                save_profile(profile)
                st.session_state.profile = profile
                st.success("Profile updated successfully!")

    # --- Page: School Research ---
    elif page == "School Research":
        st.header("🔍 School Research & Note Taking (学校调研笔记)")
        st.markdown("""
        **功能说明：**
        这是您的**手工调研笔记本**。请对照 "Department Websites" 中的官网链接，深入挖掘并记录以下关键信息。
        这些笔记将直接用于后续的 "Essay Helper" 辅助生成高质量文书。
        """)
        
        if not profile.get("target_schools"):
            st.warning("Please add target schools in the Profile tab first.")
        else:
            # 1. Select School
            selected_school = st.selectbox("Select a School to Research", profile["target_schools"])
            
            # Load existing notes
            all_notes = load_research_notes()
            school_notes = all_notes.get(selected_school, {})

            # --- Quick Links Section ---
            with st.expander("🔗 Quick Links (from Department Websites)", expanded=True):
                school_urls = profile.get("school_major_urls", {}).get(selected_school, {}).get("majors", {})
                if school_urls:
                    cols = st.columns(3)
                    idx = 0
                    for major, urls in school_urls.items():
                        with cols[idx % 3]:
                            st.markdown(f"**{major}**")
                            if urls.get("url"): st.markdown(f"• [Department Site]({urls['url']})")
                            if urls.get("faculty_url"): st.markdown(f"• [Faculty List]({urls['faculty_url']})")
                            if urls.get("courses_url"): st.markdown(f"• [Course Catalog]({urls['courses_url']})")
                            if urls.get("research_url"): st.markdown(f"• [Research/Labs]({urls['research_url']})")
                        idx += 1
                else:
                    st.info("No specific links found. Go to 'Department Websites' to auto-find them.")

            # --- Structured Note Taking ---
            st.divider()
            st.subheader(f"📝 Research Notes: {selected_school}")

            tab1, tab2, tab3, tab4, tab5 = st.tabs([
                "👨‍🏫 Professors (Faculty)", 
                "📚 Curriculum (Courses)", 
                "🔬 Research (Labs)", 
                "🏛️ Values & Mission", 
                "🎭 Student Life"
            ])

            # Helper to save
            def save_current_notes():
                all_notes[selected_school] = school_notes
                save_research_notes(all_notes)
                st.toast("Notes saved successfully!", icon="✅")

            with tab1:
                st.markdown("### Identify 1-2 professors whose work aligns with your interests.")
                st.info("💡 **提示：** 关注教授近期的论文、实验室网站或具体项目。思考为什么想与*他们*合作？")
                
                # Professors Data Editor
                prof_data = school_notes.get("professors", [])
                if not prof_data: prof_data = [{"Name": "", "Research Area": "", "Why Interesting?": ""}]
                
                edited_prof = st.data_editor(
                    prof_data,
                    num_rows="dynamic",
                    column_config={
                        "Name": st.column_config.TextColumn("Professor Name", required=True),
                        "Research Area": st.column_config.TextColumn("Research Focus", help="e.g. AI Safety, Climate Policy"),
                        "Why Interesting?": st.column_config.TextColumn("Connection to You", width="large", help="How does their work relate to your background?")
                    },
                    key=f"editor_prof_{selected_school}"
                )
                
                if edited_prof != prof_data:
                    school_notes["professors"] = edited_prof
                    save_current_notes()

            with tab2:
                st.markdown("### Find upper-level courses (300/400 level) not offered at your current school.")
                st.info("💡 **提示：** 不要只列出入门课程。寻找能弥补你知识空白的独特选修课。")
                
                course_data = school_notes.get("courses", [])
                if not course_data: course_data = [{"Course Code": "", "Course Name": "", "Relevance": ""}]
                
                edited_courses = st.data_editor(
                    course_data,
                    num_rows="dynamic",
                    column_config={
                        "Course Code": st.column_config.TextColumn("Code", help="e.g. CS 442"),
                        "Course Name": st.column_config.TextColumn("Course Name"),
                        "Relevance": st.column_config.TextColumn("Why this course?", width="large", help="What knowledge gap does this fill?")
                    },
                    key=f"editor_course_{selected_school}"
                )

                if edited_courses != course_data:
                    school_notes["courses"] = edited_courses
                    save_current_notes()

            with tab3:
                st.markdown("### Locate specific Research Labs, Centers, or Institutes.")
                st.info("💡 **提示：** 具体一点。'我想做研究' 这种说法太笼统。'我想加入 X 实验室参与 Y 项目' 会更有说服力。")
                
                lab_data = school_notes.get("research_labs", [])
                if not lab_data: lab_data = [{"Lab/Center Name": "", "Research Topic": "", "Potential Contribution": ""}]
                
                edited_labs = st.data_editor(
                    lab_data,
                    num_rows="dynamic",
                    column_config={
                        "Lab/Center Name": st.column_config.TextColumn("Lab Name", required=True),
                        "Research Topic": st.column_config.TextColumn("Topic/Focus"),
                        "Potential Contribution": st.column_config.TextColumn("Your Contribution", width="large", help="What skills can you bring?")
                    },
                    key=f"editor_labs_{selected_school}"
                )

                if edited_labs != lab_data:
                    school_notes["research_labs"] = edited_labs
                    save_current_notes()

            with tab4:
                st.markdown("### School Mission, Values, & Motto")
                st.info("💡 **提示：** 学校的'氛围'是什么？求知欲？社会正义？还是创业精神？")
                
                values_text = st.text_area(
                    "Core Values / Mission Statement Notes",
                    value=school_notes.get("values", ""),
                    height=150,
                    key=f"text_values_{selected_school}",
                    placeholder="e.g. 'Knowledge for the sake of knowledge' (UChicago), 'Mens et Manus' (MIT)..."
                )
                
                if values_text != school_notes.get("values", ""):
                    school_notes["values"] = values_text
                    save_current_notes()

            with tab5:
                st.markdown("### Student Organizations & Community")
                st.info("💡 **提示：** 寻找那些能让你延续领导力或探索新兴趣的社团。")
                
                club_data = school_notes.get("student_life", [])
                if not club_data: club_data = [{"Organization": "", "Role": "", "Impact": ""}]
                
                edited_clubs = st.data_editor(
                    club_data,
                    num_rows="dynamic",
                    column_config={
                        "Organization": st.column_config.TextColumn("Club/Org Name", required=True),
                        "Role": st.column_config.TextColumn("Role/Position"),
                        "Impact": st.column_config.TextColumn("Why join?", width="large")
                    },
                    key=f"editor_clubs_{selected_school}"
                )

                if edited_clubs != club_data:
                    school_notes["student_life"] = edited_clubs
                    save_current_notes()
                            


    # --- Page: Essay Helper ---
    elif page == "Essay Helper":
        st.header("✍️ Essay Helper (文书助手)")
        st.markdown("""
        **功能说明：**
        根据已完成的学校调研数据，自动生成 "Why Transfer" 文书大纲。
        大纲将结合你的个人背景与目标院校的独特资源（如教授、课程、社团），帮助你构建有说服力的申请文书。
        """)
        
        if not profile.get("target_schools"):
            st.warning("Please add target schools in the Profile tab first.")
        else:
            selected_school = st.selectbox("Select School for Essay", profile["target_schools"])
            
            # --- Display Essay Prompts ---
            prompts_list = load_essay_prompts()
            # Simple match
            school_prompts = next((item for item in prompts_list if item["school"] == selected_school), None)
            
            if school_prompts:
                st.subheader(f"📄 {selected_school} Transfer Essay Prompts")
                
                # Display Source Link
                source_url = school_prompts.get("source_url", "#")
                st.caption(f"🔗 [Official Source / Application Page]({source_url})")
                st.caption("⚠️ Note: Based on 2025-2026 cycle (Fall 2026 Entry). Always verify with the latest official portal.")
                
                # Wrap chat messages in a container to prevent persistence issues
                with st.container():
                    for p in school_prompts.get("prompts", []):
                        with st.chat_message("assistant"):
                            st.markdown(f"**{p['type']}**")
                            st.caption(p['word_limit'])
                            st.markdown(f"> {p['prompt']}")
                st.divider()
            else:
                st.info("No specific essay prompts found for this school yet.")
                
            # --- Outline Generation ---
            research_data = load_research_data(selected_school)
            if research_data:
                if st.button("Generate Essay Outline"):
                    with st.spinner("Generating outline..."):
                        helper = EssayHelper()
                        # Updated call signature: school_name, user_profile, research_data
                        outline = helper.generate_outline(selected_school, profile, research_data=research_data)
                        
                        st.success("Outline generated and saved!")
                        st.rerun()

                # Display existing outline
                outline_content = load_essay_outline(selected_school)
                if outline_content:
                    st.subheader("Generated Outline")
                    st.markdown(outline_content)
                    st.download_button(
                        label="Download Outline",
                        data=outline_content,
                        file_name=f"{selected_school.replace(' ', '_')}_outline.md",
                        mime="text/markdown"
                    )
            else:
                st.warning("No research data found. Please go to 'School Research' tab first.")

    # --- Page: Transfer Majors ---
    elif page == "Transfer Majors":
        st.header("🏫 Transferable Majors & Colleges (转学专业列表)")
        st.markdown("""
        **功能说明：**
        这里为您深度整理了10所目标院校的转学政策，重点按“学院（College）”划分。
        
        ⚠️ **重要提示**：
        美国顶尖大学的转学通常是录取到具体的“学院”（如工程学院、文理学院）。
        不同的学院录取难度差异巨大（例如 CMU 的 CS 学院极难，而人文学院相对友好）。
        
        请仔细阅读下方的 **Status (难度/友好度)** 和 **Notes (备注)**，选择最适合你的申请策略。
        """)
        
        # Load static data
        info_path = os.path.join("data", "school_info.json")
        if os.path.exists(info_path):
            with open(info_path, 'r', encoding='utf-8') as f:
                school_info = json.load(f)
            
            # --- SEPARATE LISTS LOGIC ---
            # 1. Prepare Data Lists
            target_school_names = profile.get("target_schools", [])
            target_schools_data = []
            other_schools_data = []
            
            # Map existing static data for easy lookup
            static_school_map = {item['school']: item for item in school_info}
            
            # A. Build Target Schools List (Mixed Static + User Added)
            for name in target_school_names:
                if name in static_school_map:
                    target_schools_data.append(static_school_map[name])
                else:
                    # Create skeleton for user-added school not in DB
                    target_schools_data.append({
                        "school": name,
                        "url": f"https://www.google.com/search?q={name.replace(' ', '+')}+transfer+admissions",
                        "colleges": [
                            {
                                "name": "General / Main College",
                                "status": "User Added",
                                "notes": "This school was added via your Profile. Specific college details are not pre-loaded.",
                                "majors_desc": "Enter your major manually below"
                            }
                        ]
                    })
            
            # B. Build Other Schools List (Static only, excluding targets)
            for item in school_info:
                if item['school'] not in target_school_names:
                    other_schools_data.append(item)
            
            # Sort lists
            target_schools_data.sort(key=lambda x: x['school'])
            other_schools_data.sort(key=lambda x: x['school'])

            # --- RENDER FUNCTION ---
            def render_school_item(school_item, section_key_prefix):
                school_name = school_item['school']
                school_url = school_item.get('url', '#')
                
                with st.expander(f"🎓 {school_name}", expanded=False):
                    st.markdown(f"🔗 [Official Transfer Admissions Page]({school_url})")
                    
                    colleges = school_item.get('colleges', [])
                    for i, college in enumerate(colleges):
                        # Unique key for this college instance
                        college_key = f"{section_key_prefix}_{school_name}_{i}"
                        
                        # Color code status
                        status = college['status']
                        status_color = "red"
                        if "Friendly" in status or "Open" in status:
                            status_color = "green"
                        elif "Specialized" in status:
                            status_color = "orange"
                        elif "User Added" in status:
                            status_color = "blue"
                        
                        st.markdown(f"#### {college['name']}")
                        st.markdown(f"**Difficulty:** :{status_color}[{status}]")
                        st.info(f"💡 **Notes:** {college['notes']}")
                        
                        with st.expander("Show Majors / Departments", expanded=False):
                            # Highlight logic
                            raw_majors = college.get('majors_desc', '')
                            if not raw_majors:
                                st.write("No major information available.")
                                continue
                                
                            majors_list = [m.strip() for m in raw_majors.split(',')]
                            
                            # Derive keywords from profile interests
                            keywords = set()
                            if "interests" in profile:
                                for interest in profile.get("interests", []):
                                    for word in interest.split():
                                        if len(word) > 3 and word.lower() not in ["and", "studies", "research", "sciences"]:
                                            keywords.add(word.lower())
                            
                            keywords.add("abe")
                            keywords.add("agricultural")
                            keywords.add("biological")
                            keywords.add("engineering")
                            keywords.add("environment")
                            
                            selection_options = []
                            major_to_clean_name = {}
                            has_star = False
                            
                            for major in majors_list:
                                is_match = False
                                for k in keywords:
                                    if k in major.lower():
                                        is_match = True
                                        break
                                
                                option_label = major
                                if is_match:
                                    option_label = f"⭐ {major}"
                                    has_star = True
                                
                                selection_options.append(option_label)
                                major_to_clean_name[option_label] = major

                            selection_options.sort(key=lambda x: (not x.startswith("⭐"), x))
                            
                            st.markdown(", ".join(selection_options))

                            if has_star:
                                st.caption("⭐ Matches your interests (Agricultural, Biological, Environment, Engineering)")
                        
                        # --- College Specific Major Input ---
                        if "college_majors" not in profile:
                            profile["college_majors"] = {}
                        if school_name not in profile["college_majors"]:
                            profile["college_majors"][school_name] = {}
                            
                        current_college_val_str = profile["college_majors"][school_name].get(college['name'], "")
                        current_selection = [m.strip() for m in current_college_val_str.split(",")] if current_college_val_str else []

                        default_options = []
                        for saved_m in current_selection:
                            found = False
                            for opt in selection_options:
                                if major_to_clean_name.get(opt) == saved_m:
                                    default_options.append(opt)
                                    found = True
                                    break
                            if not found and saved_m:
                                selection_options.append(saved_m)
                                major_to_clean_name[saved_m] = saved_m
                                default_options.append(saved_m)

                        selected_options = st.multiselect(
                            f"Select Intended Majors for {college['name']}:",
                            options=selection_options,
                            default=default_options,
                            key=f"major_select_{college_key}",
                            placeholder=f"Select majors for {college['name']}...",
                            help="Click to select majors. Selected majors will be automatically saved."
                        )
                        
                        custom_major_input = st.text_input(
                            f"Or type a custom major for {college['name']} (if not listed above):",
                            key=f"major_custom_{college_key}",
                            placeholder="e.g. specialized program not in list"
                        )

                        new_clean_majors = [major_to_clean_name.get(opt, opt) for opt in selected_options]
                        if custom_major_input.strip():
                            new_clean_majors.append(custom_major_input.strip())
                        
                        new_clean_majors = sorted(list(set(new_clean_majors)))
                        new_college_val_str = ", ".join(new_clean_majors)

                        if new_college_val_str != current_college_val_str:
                             profile["college_majors"][school_name][college['name']] = new_college_val_str
                             
                             # Aggregate all majors for this school
                             all_majors = []
                             for c_name, m_val in profile["college_majors"][school_name].items():
                                 if m_val.strip():
                                     all_majors.append(m_val.strip())
                             
                             profile["school_specific_majors"][school_name] = ", ".join(all_majors)
                             
                             save_profile(profile)
                             # Only toast if meaningful change
                             if new_college_val_str:
                                st.toast(f"Saved majors for {college['name']}")
                             st.session_state.profile = profile

                        st.divider()

            # --- DISPLAY SECTIONS ---
            if target_schools_data:
                st.subheader("🎯 My Target Schools (我的目标院校)")
                st.caption("Schools added in your Profile.")
                for item in target_schools_data:
                    render_school_item(item, "target")
                st.divider()

            if other_schools_data:
                st.subheader("📚 School Database (全部院校库)")
                st.caption("Browse other available schools.")
                for item in other_schools_data:
                    render_school_item(item, "other")



        else:
            st.warning("Data file not found.")

    # --- Page: Department Websites ---
    elif page == "Department Websites":
        st.header("🌐 Department Websites (专业官网直达)")
        st.markdown("""
        **功能说明：**
        这里展示了为您筛选的10所大学的 **专业官方网站**。
        点击链接即可直接跳转到系主页，查看最新的课程设置、教授信息和科研机会。
        
        💡 **提示**：如果列表中的链接为空，请先在 "Transfer Majors" 页面确认已输入您的目标专业，然后点击下方的 **"Auto Find Missing Websites"** 按钮。
        """)

        # Load school list from school_info.json for consistency
        info_path = os.path.join("data", "school_info.json")
        school_list = []
        if os.path.exists(info_path):
            with open(info_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                school_list = [item['school'] for item in data]
        
        # --- MERGE USER ADDED SCHOOLS ---
        if "target_schools" in profile:
            for school in profile["target_schools"]:
                if school not in school_list:
                    school_list.append(school)
        
        school_list.sort()

        # Ensure storage for URLs
        if "school_major_urls" not in profile:
            profile["school_major_urls"] = {}
            
        # --- CLEANUP ORPHANED MAJORS ---
        # Remove majors from school_major_urls that are no longer in school_specific_majors
        for school in list(profile.get("school_major_urls", {}).keys()):
            if "majors" in profile["school_major_urls"][school]:
                current_majors_str = profile.get("school_specific_majors", {}).get(school, "")
                current_majors_list = [m.strip() for m in current_majors_str.split(",") if m.strip()]
                
                # Identify keys to remove
                majors_to_remove = []
                for saved_major in profile["school_major_urls"][school]["majors"]:
                    if saved_major not in current_majors_list and saved_major != "Undecided":
                         majors_to_remove.append(saved_major)
                
                # Remove them
                for m in majors_to_remove:
                    del profile["school_major_urls"][school]["majors"][m]
                    
        # 1. Action Bar
        col_act1, col_act2 = st.columns([1, 2])
        with col_act1:
            if st.button("🔍 Auto Find Missing Websites", type="primary", help="Automatically search for official department, faculty, and course websites for schools with a set major but no URL."):
                researcher = SchoolResearcher()
                
                # Use status container for better UX
                with st.status("Searching for official websites (Dept, Faculty, Courses)...", expanded=True) as status:
                    total = len(school_list)
                    count = 0
                    updated_count = 0
                    
                    for school in school_list:
                        raw_major_str = profile.get("school_specific_majors", {}).get(school, profile.get("track", ""))
                        majors = [m.strip() for m in re.split(r'[,，]', raw_major_str) if m.strip()]
                        
                        # Initialize storage for school if not exists
                        if school not in profile["school_major_urls"]:
                            profile["school_major_urls"][school] = {}
                        
                        # Ensure 'majors' dict exists for new structure
                        if "majors" not in profile["school_major_urls"][school]:
                            profile["school_major_urls"][school]["majors"] = {}

                        for major in majors:
                            if not major or major == "Not Set": continue
                            
                            # Get current data for this major
                            major_data = profile["school_major_urls"][school]["majors"].get(major, {})
                            
                            existing_url = major_data.get("url")
                            existing_faculty_url = major_data.get("faculty_url")
                            existing_courses_url = major_data.get("courses_url")
                            existing_research_url = major_data.get("research_url")
                            
                            # 1. Find Official Dept Site
                            if not existing_url:
                                status.write(f"🔎 Searching for **{school}** ({major}) Dept Site...")
                                try:
                                    url, title = researcher.find_official_department_site(school, major)
                                    if url:
                                        if major not in profile["school_major_urls"][school]["majors"]:
                                            profile["school_major_urls"][school]["majors"][major] = {}
                                        
                                        profile["school_major_urls"][school]["majors"][major]["url"] = url
                                        profile["school_major_urls"][school]["majors"][major]["title"] = title
                                        updated_count += 1
                                        status.write(f"✅ Found Dept: [{title}]({url})")
                                    else:
                                        status.write(f"⚠️ Could not find Dept site for {school} ({major})")
                                except Exception as e:
                                    status.write(f"❌ Error searching Dept for {school}: {e}")
                            
                            # 2. Find Faculty List Site
                            if not existing_faculty_url:
                                status.write(f"🔎 Searching for **{school}** ({major}) Faculty List...")
                                try:
                                    fac_url, fac_title = researcher.find_department_faculty_page(school, major)
                                    if fac_url:
                                        if major not in profile["school_major_urls"][school]["majors"]:
                                            profile["school_major_urls"][school]["majors"][major] = {}
                                            
                                        profile["school_major_urls"][school]["majors"][major]["faculty_url"] = fac_url
                                        profile["school_major_urls"][school]["majors"][major]["faculty_title"] = fac_title
                                        updated_count += 1
                                        status.write(f"✅ Found Faculty: [{fac_title}]({fac_url})")
                                    else:
                                        status.write(f"⚠️ Could not find Faculty list for {school} ({major})")
                                except Exception as e:
                                    status.write(f"❌ Error searching Faculty for {school}: {e}")

                            # 3. Find Courses Catalog Site
                            if not existing_courses_url:
                                status.write(f"🔎 Searching for **{school}** ({major}) Course Catalog...")
                                try:
                                    course_url, course_title = researcher.find_department_courses_page(school, major)
                                    if course_url:
                                        if major not in profile["school_major_urls"][school]["majors"]:
                                            profile["school_major_urls"][school]["majors"][major] = {}
                                            
                                        profile["school_major_urls"][school]["majors"][major]["courses_url"] = course_url
                                        profile["school_major_urls"][school]["majors"][major]["courses_title"] = course_title
                                        updated_count += 1
                                        status.write(f"✅ Found Courses: [{course_title}]({course_url})")
                                    else:
                                        status.write(f"⚠️ Could not find Course Catalog for {school} ({major})")
                                except Exception as e:
                                    status.write(f"❌ Error searching Courses for {school}: {e}")

                            # 4. Find Research Labs Site
                            if not existing_research_url:
                                status.write(f"🔎 Searching for **{school}** ({major}) Research Labs...")
                                try:
                                    res_url, res_title = researcher.find_department_research_page(school, major)
                                    if res_url:
                                        if major not in profile["school_major_urls"][school]["majors"]:
                                            profile["school_major_urls"][school]["majors"][major] = {}
                                            
                                        profile["school_major_urls"][school]["majors"][major]["research_url"] = res_url
                                        profile["school_major_urls"][school]["majors"][major]["research_title"] = res_title
                                        updated_count += 1
                                        status.write(f"✅ Found Research: [{res_title}]({res_url})")
                                    else:
                                        status.write(f"⚠️ Could not find Research Labs for {school} ({major})")
                                except Exception as e:
                                    status.write(f"❌ Error searching Research Labs for {school}: {e}")
                            
                            # Small delay between majors
                            import time
                            time.sleep(0.5)
                        
                        count += 1
                        # Small delay to be polite
                        import time
                        time.sleep(0.5)
                    
                    save_profile(profile)
                    st.session_state.profile = profile
                    status.update(label=f"Search Complete! Updated {updated_count} websites.", state="complete", expanded=False)
                
                st.rerun()

        st.divider()

        # 2. Display List Table
        # Create a clean display using columns
        
        # Header
        h1, h2, h3, h4, h5, h6 = st.columns([2, 2, 2, 2, 2, 2])
        h1.markdown("**School**")
        h2.markdown("**Intended Major**")
        h3.markdown("**Official Website**")
        h4.markdown("**Faculty List**")
        h5.markdown("**Research / Labs**")
        h6.markdown("**Course Catalog**")
        st.divider()
        
        for school in school_list:
            # 3. DISPLAY (Based on current majors)
            
            # Get current majors list again
            raw_major_str = profile.get("school_specific_majors", {}).get(school, profile.get("track", ""))
            majors_to_show = [m.strip() for m in raw_major_str.split(",") if m.strip()]
            
            # If no majors, show 'Undecided' or 'Not Set'
            if not majors_to_show:
                majors_to_show = ["Not Set"]
                
            # Iterate through majors to display
            for i, major in enumerate(majors_to_show):
                
                url_info = {}
                if school in profile["school_major_urls"] and "majors" in profile["school_major_urls"][school]:
                    url_info = profile["school_major_urls"][school]["majors"].get(major, {})
                
                # Display columns
                c1, c2, c3, c4, c5, c6 = st.columns([2, 2, 2, 2, 2, 2])
                with c1:
                    if i == 0:
                        st.markdown(f"**{school}**")
                with c2:
                    if major != "Not Set":
                            st.markdown(f"{major}")
                    else:
                            st.caption("No Major Selected")
                
                # Helper for links
                def show_link(url, title, icon):
                    if url:
                        # Use URL as text if title is generic or missing, or allow user preference?
                        # Reverting to showing title as link text as per previous behavior
                        display_text = title if title else "Link"
                        if len(display_text) > 30:
                             display_text = display_text[:27] + "..."
                        st.markdown(f"{icon} [{display_text}]({url})")
                    else:
                        st.caption("-")

                with c3: show_link(url_info.get("url"), url_info.get("title", "Dept Site"), "🔗")
                with c4: show_link(url_info.get("faculty_url"), url_info.get("faculty_title", "Faculty"), "👥")
                with c5: show_link(url_info.get("research_url"), url_info.get("research_title", "Research"), "🔬")
                with c6: show_link(url_info.get("courses_url"), url_info.get("courses_title", "Courses"), "📚")
            
            st.divider()

    # --- Page: Application Tracker ---
    elif page == "Application Tracker":
        st.header("📅 Application Tracker (申请进度管理)")
        st.markdown("""
        **功能说明：**
        在此记录你针对这10所大学的申请细节，包括截止日期（Deadline）和申请专业（Intended Major）。
        """)

        if not profile.get("target_schools"):
            st.warning("Please add target schools in the Profile tab first.")
        else:
            # Load existing applications data
            apps = load_applications()
            
            # Display Summary Table
            st.subheader("📊 Application Summary")
            
            # Sort schools alphabetically
            sorted_schools = sorted(profile["target_schools"])
            
            # Cost URLs
            school_cost_urls = {
                "University of Chicago (UChicago)": "https://financialaid.uchicago.edu/undergraduate/how-aid-works/undergraduate-costs/",
                "Dartmouth College": "https://financialaid.dartmouth.edu/cost-attendance/cost-attendance-2025-2026",
                "Columbia University": "https://bulletin.columbia.edu/columbia-college/fees-expenses-financial-aid/",
                "Duke University": "https://financialaid.duke.edu/how-aid-calculated/cost-attendance/",
                "Brown University": "https://finaid.brown.edu/cost",
                "Johns Hopkins University (JHU)": "https://sfs.jhu.edu/cost-tuition/",
                "Northwestern University": "https://undergradaid.northwestern.edu/aid-basics-eligibility/cost-of-attendance.html#tab-panel2",
                "Cornell University": "https://finaid.cornell.edu/cost-to-attend",
                "University of Michigan (UMich)": "https://finaid.umich.edu/getting-started/estimating-costs",
                "Carnegie Mellon University (CMU)": "https://www.cmu.edu/sfs/tuition/undergraduate/index.html"
            }
            
            summary_data = []
            for school in sorted_schools:
                school_data = apps.get(school, {})
                summary_data.append({
                    "School": school,
                    "Cost Info": school_cost_urls.get(school, f"https://www.google.com/search?q={school.replace(' ', '+')}+cost+of+attendance"),
                    "Materials Complete": school_data.get("materials_complete", False),
                    "App Deadline": school_data.get("deadline", "Not set"),
                    "Supp Docs Deadline": school_data.get("supp_deadline", "Not set"),
                    "Decision Date": school_data.get("decision_date", "Not set"),
                    "Major": school_data.get("major", "Not set"),
                    "Status": school_data.get("status", "Not Started")
                })
            
            if summary_data:
                df = pd.DataFrame(summary_data)
                
                # Interactive Data Editor
                edited_df = st.data_editor(
                    df,
                    column_config={
                        "Materials Complete": st.column_config.CheckboxColumn(
                            "Materials Complete",
                            help="Check if all materials are submitted in the portal",
                            default=False,
                        ),
                        "Cost Info": st.column_config.LinkColumn(
                            "Cost Info",
                            display_text="View Cost"
                        )
                    },
                    disabled=["School", "Cost Info", "App Deadline", "Supp Docs Deadline", "Decision Date", "Major", "Status"],
                    hide_index=True,
                    use_container_width=True,
                    key="app_summary_editor"
                )
                
                # Check for changes in the data editor
                if not df.equals(edited_df):
                    for index, row in edited_df.iterrows():
                        school = row["School"]
                        is_complete = row["Materials Complete"]
                        
                        if school not in apps:
                            apps[school] = {}
                        
                        # Update only the checkbox status
                        apps[school]["materials_complete"] = is_complete
                    
                    save_applications(apps)
                    st.rerun()
            
            st.divider()
            st.subheader("📝 Edit Application Details")
            
            # Edit Form
            selected_school_app = st.selectbox("Select School to Edit", sorted_schools)
            
            current_app_data = apps.get(selected_school_app, {})
            
            with st.form("application_form"):
                col1, col2 = st.columns(2)
                with col1:
                    deadline = st.date_input(
                        "Application Deadline", 
                        value=pd.to_datetime(current_app_data.get("deadline", "2026-03-01"))
                    )
                    supp_deadline = st.date_input(
                        "Supporting Document Deadline", 
                        value=pd.to_datetime(current_app_data.get("supp_deadline", "2026-03-15"))
                    )
                    materials_complete = st.checkbox(
                        "All Materials Submitted (Portal Verified)",
                        value=current_app_data.get("materials_complete", False)
                    )
                with col2:
                    status = st.selectbox(
                        "Status", 
                        ["Not Started", "Researching", "Drafting Essays", "Submitted"], 
                        index=["Not Started", "Researching", "Drafting Essays", "Submitted"].index(current_app_data.get("status", "Not Started"))
                    )
                    decision_date = st.text_input(
                        "Admission Decision Notification (e.g. Mid-May)", 
                        value=current_app_data.get("decision_date", "")
                    )
                
                major_input = st.text_input("Intended Major", value=current_app_data.get("major", ""))
                notes = st.text_area("Notes", value=current_app_data.get("notes", ""))
                
                submitted_app = st.form_submit_button("Save Application Details")
                
                if submitted_app:
                    apps[selected_school_app] = {
                        "deadline": deadline.strftime("%Y-%m-%d"),
                        "supp_deadline": supp_deadline.strftime("%Y-%m-%d"),
                        "decision_date": decision_date,
                        "major": major_input,
                        "status": status,
                        "notes": notes,
                        "materials_complete": materials_complete
                    }
                    save_applications(apps)
                    st.success(f"Details for {selected_school_app} saved!")
                    st.rerun()
