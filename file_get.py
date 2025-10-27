import os
import requests
from getpass import getpass

username = os.getenv("EARTHDATA_USERNAME")
password = os.getenv("EARTHDATA_PASSWORD")


def download_merra2_files(url_list, output_dir, username, password):

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Start a session that handles redirects and cookies
    session = requests.Session()
    session.headers.update({'User-Agent': 'NASA-GESDISC-Downloader'})

    for url in url_list:
        filename = os.path.join(output_dir, os.path.basename(url))
        print(f"📥 Downloading {url} → {filename}")

        # Step 1: Try to access file (will redirect to login)
        r1 = session.get(url, allow_redirects=False)

        # Step 2: Follow redirect to URS login if needed
        if r1.status_code in [301, 302, 303, 307, 308]:
            login_url = r1.headers['Location']

            # Some links use relative redirect URLs
            if login_url.startswith('/'):
                login_url = "https://urs.earthdata.nasa.gov" + login_url

            # Step 3: Perform login
            print("🔑 Performing Earthdata login handshake...")
            r2 = session.get(login_url, auth=(username, password), allow_redirects=True)

            if r2.status_code not in [200, 302]:
                print(f"⚠️ Login failed (HTTP {r2.status_code})")
                continue

            # Step 4: Now authenticated, retry the original file request
            r3 = session.get(url, stream=True)

            if r3.status_code == 200:
                with open(filename, 'wb') as f:
                    for chunk in r3.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                print(f"✅ Saved: {filename}")
            else:
                print(f"❌ Failed to download file ({r3.status_code})")

        elif r1.status_code == 200:
            # Directly downloadable (already logged in or public)
            with open(filename, 'wb') as f:
                for chunk in r1.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            print(f"✅ Saved: {filename}")

        else:
            print(f"❌ Unexpected response {r1.status_code} for {url}")

    print("🎉 All downloads complete.")



if __name__ == "__main__":
    # Example usage:
    urls = [
"https://data.gesdisc.earthdata.nasa.gov/data/MERRA2_MONTHLY/M2TMNXLND.5.12.4/2015/MERRA2_400.tavgM_2d_lnd_Nx.201508.nc4",
"https://data.gesdisc.earthdata.nasa.gov/data/MERRA2_MONTHLY/M2TMNXLND.5.12.4/2015/MERRA2_400.tavgM_2d_lnd_Nx.201509.nc4",
"https://data.gesdisc.earthdata.nasa.gov/data/MERRA2_MONTHLY/M2TMNXLND.5.12.4/2015/MERRA2_400.tavgM_2d_lnd_Nx.201510.nc4",
"https://data.gesdisc.earthdata.nasa.gov/data/MERRA2_MONTHLY/M2TMNXLND.5.12.4/2015/MERRA2_400.tavgM_2d_lnd_Nx.201511.nc4",
"https://data.gesdisc.earthdata.nasa.gov/data/MERRA2_MONTHLY/M2TMNXLND.5.12.4/2015/MERRA2_400.tavgM_2d_lnd_Nx.201512.nc4",
"https://data.gesdisc.earthdata.nasa.gov/data/MERRA2_MONTHLY/M2TMNXLND.5.12.4/2016/MERRA2_400.tavgM_2d_lnd_Nx.201601.nc4",
"https://data.gesdisc.earthdata.nasa.gov/data/MERRA2_MONTHLY/M2TMNXLND.5.12.4/2016/MERRA2_400.tavgM_2d_lnd_Nx.201602.nc4",
"https://data.gesdisc.earthdata.nasa.gov/data/MERRA2_MONTHLY/M2TMNXLND.5.12.4/2016/MERRA2_400.tavgM_2d_lnd_Nx.201603.nc4",
"https://data.gesdisc.earthdata.nasa.gov/data/MERRA2_MONTHLY/M2TMNXLND.5.12.4/2016/MERRA2_400.tavgM_2d_lnd_Nx.201604.nc4",
"https://data.gesdisc.earthdata.nasa.gov/data/MERRA2_MONTHLY/M2TMNXLND.5.12.4/2016/MERRA2_400.tavgM_2d_lnd_Nx.201605.nc4",
"https://data.gesdisc.earthdata.nasa.gov/data/MERRA2_MONTHLY/M2TMNXLND.5.12.4/2016/MERRA2_400.tavgM_2d_lnd_Nx.201606.nc4",
"https://data.gesdisc.earthdata.nasa.gov/data/MERRA2_MONTHLY/M2TMNXLND.5.12.4/2016/MERRA2_400.tavgM_2d_lnd_Nx.201607.nc4",
"https://data.gesdisc.earthdata.nasa.gov/data/MERRA2_MONTHLY/M2TMNXLND.5.12.4/2016/MERRA2_400.tavgM_2d_lnd_Nx.201608.nc4",
"https://data.gesdisc.earthdata.nasa.gov/data/MERRA2_MONTHLY/M2TMNXLND.5.12.4/2016/MERRA2_400.tavgM_2d_lnd_Nx.201609.nc4",
"https://data.gesdisc.earthdata.nasa.gov/data/MERRA2_MONTHLY/M2TMNXLND.5.12.4/2016/MERRA2_400.tavgM_2d_lnd_Nx.201610.nc4",
"https://data.gesdisc.earthdata.nasa.gov/data/MERRA2_MONTHLY/M2TMNXLND.5.12.4/2016/MERRA2_400.tavgM_2d_lnd_Nx.201611.nc4",
"https://data.gesdisc.earthdata.nasa.gov/data/MERRA2_MONTHLY/M2TMNXLND.5.12.4/2016/MERRA2_400.tavgM_2d_lnd_Nx.201612.nc4",
"https://data.gesdisc.earthdata.nasa.gov/data/MERRA2_MONTHLY/M2TMNXLND.5.12.4/2017/MERRA2_400.tavgM_2d_lnd_Nx.201701.nc4",
"https://data.gesdisc.earthdata.nasa.gov/data/MERRA2_MONTHLY/M2TMNXLND.5.12.4/2017/MERRA2_400.tavgM_2d_lnd_Nx.201702.nc4",
"https://data.gesdisc.earthdata.nasa.gov/data/MERRA2_MONTHLY/M2TMNXLND.5.12.4/2017/MERRA2_400.tavgM_2d_lnd_Nx.201703.nc4",
"https://data.gesdisc.earthdata.nasa.gov/data/MERRA2_MONTHLY/M2TMNXLND.5.12.4/2017/MERRA2_400.tavgM_2d_lnd_Nx.201704.nc4",
"https://data.gesdisc.earthdata.nasa.gov/data/MERRA2_MONTHLY/M2TMNXLND.5.12.4/2017/MERRA2_400.tavgM_2d_lnd_Nx.201705.nc4",
"https://data.gesdisc.earthdata.nasa.gov/data/MERRA2_MONTHLY/M2TMNXLND.5.12.4/2017/MERRA2_400.tavgM_2d_lnd_Nx.201706.nc4",
"https://data.gesdisc.earthdata.nasa.gov/data/MERRA2_MONTHLY/M2TMNXLND.5.12.4/2017/MERRA2_400.tavgM_2d_lnd_Nx.201707.nc4",
"https://data.gesdisc.earthdata.nasa.gov/data/MERRA2_MONTHLY/M2TMNXLND.5.12.4/2017/MERRA2_400.tavgM_2d_lnd_Nx.201708.nc4",
"https://data.gesdisc.earthdata.nasa.gov/data/MERRA2_MONTHLY/M2TMNXLND.5.12.4/2017/MERRA2_400.tavgM_2d_lnd_Nx.201709.nc4",
"https://data.gesdisc.earthdata.nasa.gov/data/MERRA2_MONTHLY/M2TMNXLND.5.12.4/2017/MERRA2_400.tavgM_2d_lnd_Nx.201710.nc4",
"https://data.gesdisc.earthdata.nasa.gov/data/MERRA2_MONTHLY/M2TMNXLND.5.12.4/2017/MERRA2_400.tavgM_2d_lnd_Nx.201711.nc4",
"https://data.gesdisc.earthdata.nasa.gov/data/MERRA2_MONTHLY/M2TMNXLND.5.12.4/2017/MERRA2_400.tavgM_2d_lnd_Nx.201712.nc4",
"https://data.gesdisc.earthdata.nasa.gov/data/MERRA2_MONTHLY/M2TMNXLND.5.12.4/2018/MERRA2_400.tavgM_2d_lnd_Nx.201801.nc4",
"https://data.gesdisc.earthdata.nasa.gov/data/MERRA2_MONTHLY/M2TMNXLND.5.12.4/2018/MERRA2_400.tavgM_2d_lnd_Nx.201802.nc4",
"https://data.gesdisc.earthdata.nasa.gov/data/MERRA2_MONTHLY/M2TMNXLND.5.12.4/2018/MERRA2_400.tavgM_2d_lnd_Nx.201803.nc4",
"https://data.gesdisc.earthdata.nasa.gov/data/MERRA2_MONTHLY/M2TMNXLND.5.12.4/2018/MERRA2_400.tavgM_2d_lnd_Nx.201804.nc4",
"https://data.gesdisc.earthdata.nasa.gov/data/MERRA2_MONTHLY/M2TMNXLND.5.12.4/2018/MERRA2_400.tavgM_2d_lnd_Nx.201805.nc4",
"https://data.gesdisc.earthdata.nasa.gov/data/MERRA2_MONTHLY/M2TMNXLND.5.12.4/2018/MERRA2_400.tavgM_2d_lnd_Nx.201806.nc4",
"https://data.gesdisc.earthdata.nasa.gov/data/MERRA2_MONTHLY/M2TMNXLND.5.12.4/2018/MERRA2_400.tavgM_2d_lnd_Nx.201807.nc4",
"https://data.gesdisc.earthdata.nasa.gov/data/MERRA2_MONTHLY/M2TMNXLND.5.12.4/2018/MERRA2_400.tavgM_2d_lnd_Nx.201808.nc4",
"https://data.gesdisc.earthdata.nasa.gov/data/MERRA2_MONTHLY/M2TMNXLND.5.12.4/2018/MERRA2_400.tavgM_2d_lnd_Nx.201809.nc4",
"https://data.gesdisc.earthdata.nasa.gov/data/MERRA2_MONTHLY/M2TMNXLND.5.12.4/2018/MERRA2_400.tavgM_2d_lnd_Nx.201810.nc4",
"https://data.gesdisc.earthdata.nasa.gov/data/MERRA2_MONTHLY/M2TMNXLND.5.12.4/2018/MERRA2_400.tavgM_2d_lnd_Nx.201811.nc4",
"https://data.gesdisc.earthdata.nasa.gov/data/MERRA2_MONTHLY/M2TMNXLND.5.12.4/2018/MERRA2_400.tavgM_2d_lnd_Nx.201812.nc4",
"https://data.gesdisc.earthdata.nasa.gov/data/MERRA2_MONTHLY/M2TMNXLND.5.12.4/2019/MERRA2_400.tavgM_2d_lnd_Nx.201901.nc4",
"https://data.gesdisc.earthdata.nasa.gov/data/MERRA2_MONTHLY/M2TMNXLND.5.12.4/2019/MERRA2_400.tavgM_2d_lnd_Nx.201902.nc4",
"https://data.gesdisc.earthdata.nasa.gov/data/MERRA2_MONTHLY/M2TMNXLND.5.12.4/2019/MERRA2_400.tavgM_2d_lnd_Nx.201903.nc4",
"https://data.gesdisc.earthdata.nasa.gov/data/MERRA2_MONTHLY/M2TMNXLND.5.12.4/2019/MERRA2_400.tavgM_2d_lnd_Nx.201904.nc4",
"https://data.gesdisc.earthdata.nasa.gov/data/MERRA2_MONTHLY/M2TMNXLND.5.12.4/2019/MERRA2_400.tavgM_2d_lnd_Nx.201905.nc4",
"https://data.gesdisc.earthdata.nasa.gov/data/MERRA2_MONTHLY/M2TMNXLND.5.12.4/2019/MERRA2_400.tavgM_2d_lnd_Nx.201906.nc4",
"https://data.gesdisc.earthdata.nasa.gov/data/MERRA2_MONTHLY/M2TMNXLND.5.12.4/2019/MERRA2_400.tavgM_2d_lnd_Nx.201907.nc4",
"https://data.gesdisc.earthdata.nasa.gov/data/MERRA2_MONTHLY/M2TMNXLND.5.12.4/2019/MERRA2_400.tavgM_2d_lnd_Nx.201908.nc4",
"https://data.gesdisc.earthdata.nasa.gov/data/MERRA2_MONTHLY/M2TMNXLND.5.12.4/2019/MERRA2_400.tavgM_2d_lnd_Nx.201909.nc4",
"https://data.gesdisc.earthdata.nasa.gov/data/MERRA2_MONTHLY/M2TMNXLND.5.12.4/2019/MERRA2_400.tavgM_2d_lnd_Nx.201910.nc4",
"https://data.gesdisc.earthdata.nasa.gov/data/MERRA2_MONTHLY/M2TMNXLND.5.12.4/2019/MERRA2_400.tavgM_2d_lnd_Nx.201911.nc4",
"https://data.gesdisc.earthdata.nasa.gov/data/MERRA2_MONTHLY/M2TMNXLND.5.12.4/2019/MERRA2_400.tavgM_2d_lnd_Nx.201912.nc4",
"https://data.gesdisc.earthdata.nasa.gov/data/MERRA2_MONTHLY/M2TMNXLND.5.12.4/2020/MERRA2_400.tavgM_2d_lnd_Nx.202001.nc4",
"https://data.gesdisc.earthdata.nasa.gov/data/MERRA2_MONTHLY/M2TMNXLND.5.12.4/2020/MERRA2_400.tavgM_2d_lnd_Nx.202002.nc4",
"https://data.gesdisc.earthdata.nasa.gov/data/MERRA2_MONTHLY/M2TMNXLND.5.12.4/2020/MERRA2_400.tavgM_2d_lnd_Nx.202003.nc4",
"https://data.gesdisc.earthdata.nasa.gov/data/MERRA2_MONTHLY/M2TMNXLND.5.12.4/2020/MERRA2_400.tavgM_2d_lnd_Nx.202004.nc4",
"https://data.gesdisc.earthdata.nasa.gov/data/MERRA2_MONTHLY/M2TMNXLND.5.12.4/2020/MERRA2_400.tavgM_2d_lnd_Nx.202005.nc4",
"https://data.gesdisc.earthdata.nasa.gov/data/MERRA2_MONTHLY/M2TMNXLND.5.12.4/2020/MERRA2_400.tavgM_2d_lnd_Nx.202006.nc4",
"https://data.gesdisc.earthdata.nasa.gov/data/MERRA2_MONTHLY/M2TMNXLND.5.12.4/2020/MERRA2_400.tavgM_2d_lnd_Nx.202007.nc4",
"https://data.gesdisc.earthdata.nasa.gov/data/MERRA2_MONTHLY/M2TMNXLND.5.12.4/2020/MERRA2_400.tavgM_2d_lnd_Nx.202008.nc4",
"https://data.gesdisc.earthdata.nasa.gov/data/MERRA2_MONTHLY/M2TMNXLND.5.12.4/2020/MERRA2_401.tavgM_2d_lnd_Nx.202009.nc4",
"https://data.gesdisc.earthdata.nasa.gov/data/MERRA2_MONTHLY/M2TMNXLND.5.12.4/2020/MERRA2_400.tavgM_2d_lnd_Nx.202010.nc4",
"https://data.gesdisc.earthdata.nasa.gov/data/MERRA2_MONTHLY/M2TMNXLND.5.12.4/2020/MERRA2_400.tavgM_2d_lnd_Nx.202011.nc4",
"https://data.gesdisc.earthdata.nasa.gov/data/MERRA2_MONTHLY/M2TMNXLND.5.12.4/2020/MERRA2_400.tavgM_2d_lnd_Nx.202012.nc4",
"https://data.gesdisc.earthdata.nasa.gov/data/MERRA2_MONTHLY/M2TMNXLND.5.12.4/2021/MERRA2_400.tavgM_2d_lnd_Nx.202101.nc4",
"https://data.gesdisc.earthdata.nasa.gov/data/MERRA2_MONTHLY/M2TMNXLND.5.12.4/2021/MERRA2_400.tavgM_2d_lnd_Nx.202102.nc4",
"https://data.gesdisc.earthdata.nasa.gov/data/MERRA2_MONTHLY/M2TMNXLND.5.12.4/2021/MERRA2_400.tavgM_2d_lnd_Nx.202103.nc4",
"https://data.gesdisc.earthdata.nasa.gov/data/MERRA2_MONTHLY/M2TMNXLND.5.12.4/2021/MERRA2_400.tavgM_2d_lnd_Nx.202104.nc4",
"https://data.gesdisc.earthdata.nasa.gov/data/MERRA2_MONTHLY/M2TMNXLND.5.12.4/2021/MERRA2_400.tavgM_2d_lnd_Nx.202105.nc4",
"https://data.gesdisc.earthdata.nasa.gov/data/MERRA2_MONTHLY/M2TMNXLND.5.12.4/2021/MERRA2_401.tavgM_2d_lnd_Nx.202106.nc4",
"https://data.gesdisc.earthdata.nasa.gov/data/MERRA2_MONTHLY/M2TMNXLND.5.12.4/2021/MERRA2_401.tavgM_2d_lnd_Nx.202107.nc4",
"https://data.gesdisc.earthdata.nasa.gov/data/MERRA2_MONTHLY/M2TMNXLND.5.12.4/2021/MERRA2_401.tavgM_2d_lnd_Nx.202108.nc4",
"https://data.gesdisc.earthdata.nasa.gov/data/MERRA2_MONTHLY/M2TMNXLND.5.12.4/2021/MERRA2_401.tavgM_2d_lnd_Nx.202109.nc4",
"https://data.gesdisc.earthdata.nasa.gov/data/MERRA2_MONTHLY/M2TMNXLND.5.12.4/2021/MERRA2_400.tavgM_2d_lnd_Nx.202110.nc4",
"https://data.gesdisc.earthdata.nasa.gov/data/MERRA2_MONTHLY/M2TMNXLND.5.12.4/2021/MERRA2_400.tavgM_2d_lnd_Nx.202111.nc4",
"https://data.gesdisc.earthdata.nasa.gov/data/MERRA2_MONTHLY/M2TMNXLND.5.12.4/2021/MERRA2_400.tavgM_2d_lnd_Nx.202112.nc4",
"https://data.gesdisc.earthdata.nasa.gov/data/MERRA2_MONTHLY/M2TMNXLND.5.12.4/2022/MERRA2_400.tavgM_2d_lnd_Nx.202201.nc4",
"https://data.gesdisc.earthdata.nasa.gov/data/MERRA2_MONTHLY/M2TMNXLND.5.12.4/2022/MERRA2_400.tavgM_2d_lnd_Nx.202202.nc4",
"https://data.gesdisc.earthdata.nasa.gov/data/MERRA2_MONTHLY/M2TMNXLND.5.12.4/2022/MERRA2_400.tavgM_2d_lnd_Nx.202203.nc4",
"https://data.gesdisc.earthdata.nasa.gov/data/MERRA2_MONTHLY/M2TMNXLND.5.12.4/2022/MERRA2_400.tavgM_2d_lnd_Nx.202204.nc4",
"https://data.gesdisc.earthdata.nasa.gov/data/MERRA2_MONTHLY/M2TMNXLND.5.12.4/2022/MERRA2_400.tavgM_2d_lnd_Nx.202205.nc4",
"https://data.gesdisc.earthdata.nasa.gov/data/MERRA2_MONTHLY/M2TMNXLND.5.12.4/2022/MERRA2_400.tavgM_2d_lnd_Nx.202206.nc4",
"https://data.gesdisc.earthdata.nasa.gov/data/MERRA2_MONTHLY/M2TMNXLND.5.12.4/2022/MERRA2_400.tavgM_2d_lnd_Nx.202207.nc4",
"https://data.gesdisc.earthdata.nasa.gov/data/MERRA2_MONTHLY/M2TMNXLND.5.12.4/2022/MERRA2_400.tavgM_2d_lnd_Nx.202208.nc4",
"https://data.gesdisc.earthdata.nasa.gov/data/MERRA2_MONTHLY/M2TMNXLND.5.12.4/2022/MERRA2_400.tavgM_2d_lnd_Nx.202209.nc4",
"https://data.gesdisc.earthdata.nasa.gov/data/MERRA2_MONTHLY/M2TMNXLND.5.12.4/2022/MERRA2_400.tavgM_2d_lnd_Nx.202210.nc4",
"https://data.gesdisc.earthdata.nasa.gov/data/MERRA2_MONTHLY/M2TMNXLND.5.12.4/2022/MERRA2_400.tavgM_2d_lnd_Nx.202211.nc4",
"https://data.gesdisc.earthdata.nasa.gov/data/MERRA2_MONTHLY/M2TMNXLND.5.12.4/2022/MERRA2_400.tavgM_2d_lnd_Nx.202212.nc4",
"https://data.gesdisc.earthdata.nasa.gov/data/MERRA2_MONTHLY/M2TMNXLND.5.12.4/2023/MERRA2_400.tavgM_2d_lnd_Nx.202301.nc4",
"https://data.gesdisc.earthdata.nasa.gov/data/MERRA2_MONTHLY/M2TMNXLND.5.12.4/2023/MERRA2_400.tavgM_2d_lnd_Nx.202302.nc4",
"https://data.gesdisc.earthdata.nasa.gov/data/MERRA2_MONTHLY/M2TMNXLND.5.12.4/2023/MERRA2_400.tavgM_2d_lnd_Nx.202303.nc4",
"https://data.gesdisc.earthdata.nasa.gov/data/MERRA2_MONTHLY/M2TMNXLND.5.12.4/2023/MERRA2_400.tavgM_2d_lnd_Nx.202304.nc4",
"https://data.gesdisc.earthdata.nasa.gov/data/MERRA2_MONTHLY/M2TMNXLND.5.12.4/2023/MERRA2_400.tavgM_2d_lnd_Nx.202305.nc4",
"https://data.gesdisc.earthdata.nasa.gov/data/MERRA2_MONTHLY/M2TMNXLND.5.12.4/2023/MERRA2_400.tavgM_2d_lnd_Nx.202306.nc4",
"https://data.gesdisc.earthdata.nasa.gov/data/MERRA2_MONTHLY/M2TMNXLND.5.12.4/2023/MERRA2_400.tavgM_2d_lnd_Nx.202307.nc4",
"https://data.gesdisc.earthdata.nasa.gov/data/MERRA2_MONTHLY/M2TMNXLND.5.12.4/2023/MERRA2_400.tavgM_2d_lnd_Nx.202308.nc4",
"https://data.gesdisc.earthdata.nasa.gov/data/MERRA2_MONTHLY/M2TMNXLND.5.12.4/2023/MERRA2_400.tavgM_2d_lnd_Nx.202309.nc4",
"https://data.gesdisc.earthdata.nasa.gov/data/MERRA2_MONTHLY/M2TMNXLND.5.12.4/2023/MERRA2_400.tavgM_2d_lnd_Nx.202310.nc4",
"https://data.gesdisc.earthdata.nasa.gov/data/MERRA2_MONTHLY/M2TMNXLND.5.12.4/2023/MERRA2_400.tavgM_2d_lnd_Nx.202311.nc4",
"https://data.gesdisc.earthdata.nasa.gov/data/MERRA2_MONTHLY/M2TMNXLND.5.12.4/2023/MERRA2_400.tavgM_2d_lnd_Nx.202312.nc4"
    ]

    output_folder = r"C:\Users\Maxcu\LizTakeover\Classes\CSCI4502\Project\merra2_data"
    download_merra2_files(urls, output_folder, username, password)
