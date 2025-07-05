import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import warnings
from datetime import datetime, timedelta, time
from pathlib import Path

st.set_page_config(
layout="wide" # Sets the layout to wide mode
)
warnings.filterwarnings('ignore')
st.title("📈 Bioreactor Trend Plotter")

col1, col2 = st.columns([0.3, 0.7])

with col1:
    #upload .CSV file
    uploaded_file = st.file_uploader("上傳原始 CSV 檔案", type="csv")
    (start_time, final_time) = (None, None)
    if uploaded_file:
        Data = pd.read_csv(uploaded_file)
        #start_time = st.text_input("start time: ")
        
        start_date = st.date_input("start time:", value=None)
        
        if start_date is not None:
            # 轉成 datetime，再格式化為指定格式
            start_time_combine = datetime.combine(start_date, datetime.min.time())
            start_time = start_time_combine.strftime("%Y/%m/%d %H:%M")
            #st.write("start_time:", start_time)
            DAYS = st.text_input("Culture Length (day): ")
            
            #st.write("DAYS", DAYS)
            #cut_time = st.toggle("input final time")
            cut_time = st.time_input("final time: ", value=time(23, 59))
            if DAYS:
                    DAYS = int(DAYS)
                    final_date = start_date + timedelta(days=DAYS)
                    final_time_combine = datetime.combine(final_date, cut_time)
                    #final_time_combine = datetime.combine(final_date, time(23,59))
                    final_time = final_time_combine.strftime("%Y/%m/%d %H:%M")         

        st.write("final_time", final_time)
        add_base = st.toggle("有加鹼？")
        
    ##################修改Timestamp格式###################

with col2:
    if uploaded_file and start_date and DAYS:
    # 確保第一欄是第一個欄位（index 0）
        first_col = Data.columns[0]
    # 顯示原始資料
        st.subheader("原始資料")
        st.dataframe(Data, height = 200)
    # 處理第一欄資料
        Data[first_col] = Data[first_col].astype(str)  # 確保是字串
        Data[first_col] = Data[first_col].str.replace('T', ' ', regex=False)
    # 轉換為 datetime 格式再轉回指定字串格式，確保月份與日期都是兩位
        Data[first_col] = pd.to_datetime(Data[first_col], errors='coerce').dt.strftime('%Y/%m/%d %H:%M')
    # 重命名欄位
        rename_dict = {
            'm_mfc2': 'Air (ccm)',
            'm_mfc3': 'O2 (ccm)',
            'm_do': 'DO (%)',
            'm_mfc4': 'CO2 (ccm)',
            'm_ph': 'pH',
            'm_stirrer': 'Agitation (rpm)',
            'm_temp': 'Temperature (degC)',
            'Timestamp': 'Time (h)'
            }
        if add_base:
            rename_dict['dm_dpump2'] = 'Base (mL)'
        Data = Data.rename(columns=rename_dict)
        Data = Data.fillna(method='ffill')
    # The command then take the slice containing only the data after the start time
        timeRange_index = (
            Data[(Data['Time (h)'] > start_time) & (Data['Time (h)'] < final_time)].index.values
            if final_time is not None and not pd.isna(final_time)
            else Data[Data['Time (h)'] > start_time].index.values
            )

    # Print out the indexes
        print("Indexes included in the analysis: {}".format(timeRange_index))
    # Show the head of the data frame
        Data = Data.iloc[timeRange_index]
    # Based on the format of the date time you're using, convert the data type to datetime
        Data['Time (h)'] = pd.to_datetime(Data['Time (h)'], format='%Y/%m/%d %H:%M')
    # Add a new column that shows the time lapse with "hour" as the unit
        Data['ElapsedTime (h)'] = (Data['Time (h)'] - Data['Time (h)'] [timeRange_index[0]])/np.timedelta64(1, 'h')
        Data = Data.set_index('Time (h)')
        
    # 顯示處理後資料
        #postProcessed = True
        st.write("Data processing done!")
        st.subheader("處理後資料")
        st.dataframe(Data, height = 200)
                # 下載處理後 CSV
        csv = Data.to_csv(index=False).encode('utf-8')
        st.download_button("下載處理後 CSV", csv, file_name="processed.csv", mime="text/csv")

if uploaded_file and start_date and DAYS:
        col3, col4 = st.columns([0.3, 0.7])

            # 畫圖
            # Export the trend graph
        fig, host = plt.subplots(figsize=(12, 5)) # host: m_temp
        ################################################################################################
        # Twin axes definition
        O2 = host.twinx() # O2 flow
        CO2 = host.twinx() # CO2 flow
        Air = host.twinx() # Air flow
        Stirrer = host.twinx() # stirrer
        pH = host.twinx() # pH
        DO = host.twinx() # DO
        if add_base:
            Base = host.twinx() # Base

        with col3:
        
            st.subheader("Axis range")
            host.set_xlim(0, 24*DAYS)
            host.set_xticks([i*24 for i in range(DAYS + 2)]) # Set the tick mark interval to be 24
            (TEMP_LB, TEMP_UB) = (0, 40)
            host.set_ylim(TEMP_LB, TEMP_UB)
            (O2_LB, O2_UB) = st.slider("O2 (ccm)", 0, 1000, (0, 500), step = 100)
            (CO2_LB, CO2_UB) = st.slider("CO2 (ccm)", 0, 1000, (0, 500), step = 100)
            (AIR_LB, AIR_UB) = st.slider("Air (ccm)", 0, 1000, (0, 500), step = 100)
            (DO_LB, DO_UB) = st.slider("DO (%)", 0, 200, (0, 120), step = 10)
            (STIR_LB, STIR_UB) = st.slider("Stirrer (rpm)", 0, 2000, (0, 500), step = 100)
            (PH_LB, PH_UB) = st.slider("pH", 4.0, 8.0, (4.0, 8.0), step = 0.1)
            if add_base:
                (Base_LB, Base_UB) = st.slider("Base (mL)", 0, 500, (0, 100), step = 10)
                Base.set_ylim(Base_LB, Base_UB)
            O2.set_ylim(O2_LB, O2_UB)
            CO2.set_ylim(CO2_LB, CO2_UB)
            Air.set_ylim(AIR_LB, AIR_UB)
            Stirrer.set_ylim(STIR_LB, STIR_UB)
            pH.set_ylim(PH_LB, PH_UB)
            DO.set_ylim(DO_LB, DO_UB)
               

        ################################################################################################
        # Set the labels
            host.set_xlabel('ElapsedTime (h)')
            host.set_ylabel('Temperature ($^\circ$C)')
            CO2.set_ylabel('$CO_2$ (ccm)')
            O2.set_ylabel('$O_2$ (ccm)')
            Air.set_ylabel('Air (ccm)')
            Stirrer.set_ylabel('Agitation(rpm)')
            pH.set_ylabel('pH')
            DO.set_ylabel('DO (%)')
            if add_base:
                Base.set_ylabel('Base (mL)')

        ################################################################################################
        # Plot
            pTemp, = host.plot(Data['ElapsedTime (h)'],
                               Data['Temperature (degC)'],
                               color='k',
                               linewidth=0.5)
            pO2, = O2.plot(Data['ElapsedTime (h)'],
                           Data['O2 (ccm)'],
                           color='#2ca02c',
                           linewidth=0.5)
            pCO2, = CO2.plot(Data['ElapsedTime (h)'],
                             Data['CO2 (ccm)'],
                             color='#8c564b',
                             linewidth=0.5,
                             alpha = 0.8)
            pAir, = Air.plot(Data['ElapsedTime (h)'],
                             Data['Air (ccm)'],
                             color='#1f77b4',
                             linewidth=0.7)
            pStirrer, = Stirrer.plot(Data['ElapsedTime (h)'],
                                     Data['Agitation (rpm)'],
                                     color='#39AAAD',
                                     linewidth=0.9)
            ppH, = pH.plot(Data['ElapsedTime (h)'],
                           Data['pH'],
                           color='#d62728',
                           linewidth=0.5)
            pDO, = DO.plot(Data['ElapsedTime (h)'],
                           Data['DO (%)'],
                           color='b',
                           linewidth=0.5,
                           alpha=0.7)
            if add_base:
                pBase, = Base.plot(Data['ElapsedTime (h)'],
                                   Data['Base (mL)'],
                                   color='purple',
                                   linewidth=0.5)
        ################################################################################################
        # Twin axes
            OUTWARD_OFFSET = 50
            CO2.spines['right'].set_position(('outward', 1))
            CO2.spines['right'].set_color(pCO2.get_color())

            O2.spines['right'].set_position(('outward', OUTWARD_OFFSET))
            O2.spines['right'].set_color(pO2.get_color())

            Air.spines['right'].set_position(('outward', OUTWARD_OFFSET*2))
            Air.spines['right'].set_color(pAir.get_color())

            if add_base:
                Base.spines['right'].set_position(('outward', OUTWARD_OFFSET*3))
                Base.spines['right'].set_color(pBase.get_color())

            Stirrer.spines['left'].set_position(('outward', OUTWARD_OFFSET))
            Stirrer.yaxis.set_label_position('left')
            Stirrer.yaxis.set_ticks_position('left')
            Stirrer.spines['left'].set_color(pStirrer.get_color())

            pH.spines['left'].set_position(('outward', OUTWARD_OFFSET*2))
            pH.yaxis.set_label_position('left')
            pH.yaxis.set_ticks_position('left')
            pH.spines['left'].set_color(ppH.get_color())

            DO.spines['left'].set_position(('outward', OUTWARD_OFFSET*3))
            DO.yaxis.set_label_position('left')
            DO.yaxis.set_ticks_position('left')
            DO.spines['left'].set_color(pDO.get_color())

        ################################################################################################
        # Label colors
            axs = [host, CO2, O2, Air, Stirrer, pH, DO]
            pvars = [pTemp, pCO2, pO2, pAir, pStirrer, ppH, pDO]
            for (ax, pvar) in zip(axs, pvars):
                    ax.yaxis.label.set_color(pvar.get_color())
                    ax.tick_params(axis='y', colors=pvar.get_color())
                    if add_base:
                        Base.yaxis.label.set_color(pBase.get_color())

        with col4:
        ################################################################################################
        # Export the trend-graph
            host.grid(which='both',linestyle='--')
            plt.tight_layout()
            #fig.savefig(exportFigure_name, dpi=300)    

            st.subheader("Trend Graph")

            #fig, host = plt.subplots()
            #ax.plot(Data['Time (h)'], df['pH'], label="pH")
            #ax.set_xlabel("Time (h)")
            #ax.set_ylabel("pH")
            #ax.set_title("pH Trend")
            #ax.legend()
            st.pyplot(fig)

            
