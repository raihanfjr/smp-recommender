import flask
import difflib
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.decomposition import PCA
from sklearn.preprocessing import LabelEncoder
from sklearn.preprocessing import MinMaxScaler
from sklearn.cluster import AgglomerativeClustering
from sklearn.metrics.pairwise import cosine_similarity

app = flask.Flask(__name__, template_folder='templates')

data = pd.read_csv('./model/DataSMP.csv')
indices = pd.Series(data.index, index=data['Nama Sekolah'])
all_titles = [data['Nama Sekolah'][i] for i in range(len(data['Nama Sekolah']))]

def get_recommendations(title):
    idx = indices[title]
    new_row = data.iloc[idx,:]    
    # new_data = data.loc[data["Clusters"] == new_row["Clusters"]].append(new_row, ignore_index=True)
    new_data = data.append(new_row, ignore_index=True)
    sim_scores = cosine_similarity(new_data[new_data.columns.difference(["Nama Sekolah", "Unnamed: 0"])])
    score = []
    for rate in sim_scores[-1]:
        score.append(rate/(sim_scores[-1].sum()-1))
    new_data['Score'] = score
    dummies = new_data[new_data.columns.difference(["Nama Sekolah", "Peserta Didik", "Rombongan Belajar", "Guru", "Pegawai","R. Kelas", "R. Lab", "R. Perpus", "Unnamed: 0", "Clusters", "Status", "Latitude", "Langitude"])]
    dummies = dummies.idxmax(axis=1)
    new_data["Kecamatan"]= dummies    
    # result = new_data.iloc[:252,:].sort_values(by=['Score'], ascending=False).iloc[0:10,:]
    new_data = new_data.iloc[:252,:].sort_values(by=['Score'], ascending=False).iloc[0:,:]

    new_row = new_data.iloc[0,:]
    result = new_data.loc[new_data["Kecamatan"] == new_row["Kecamatan"]]
    if(len(result)<10):
        result2 = new_data.loc[new_data["Kecamatan"] != new_row["Kecamatan"]].iloc[:10-len(result),:]
        frames = [result, result2]
        result = pd.concat(frames)
    else:
        result =  result.iloc[:10,:]
    print(new_data)          
    
    return result[["Nama Sekolah", "Peserta Didik", "Rombongan Belajar", "Guru", "Pegawai","R. Kelas", "R. Lab", "R. Perpus", "Kecamatan"]]


# Set up the main route
@app.route('/', methods=['GET', 'POST'])

def main():
    if flask.request.method == 'GET':
        return(flask.render_template('index.html'))
            
    if flask.request.method == 'POST':
        s_name = flask.request.form['school_name']
        s_name = s_name.title().upper()
        if s_name not in all_titles:
            return(flask.render_template('negative.html',name=s_name))
        else:
            result_final = get_recommendations(s_name)
            names = []
            pesdik = []
            rombel = []
            guru = []
            pegawai = []
            clscount = []
            labcount = []
            libcount = []
            region = []
            for i in range(len(result_final)):
                names.append(result_final.iloc[i][0])
                pesdik.append(result_final.iloc[i][1])
                rombel.append(result_final.iloc[i][2])
                guru.append(result_final.iloc[i][3])
                pegawai.append(result_final.iloc[i][4])
                clscount.append(result_final.iloc[i][5])
                labcount.append(result_final.iloc[i][6])
                libcount.append(result_final.iloc[i][7])
                region.append(result_final.iloc[i][8])

            return flask.render_template(
                'positive.html',
                school_names=names,
                pesdik=pesdik,
                rombel=rombel,
                guru=guru,
                pegawai=pegawai,
                cls_count=clscount,
                lab_count=labcount,
                lib_count=libcount,
                region=region,
                search_name=s_name)

if __name__ == '__main__':
    app.debug = True
    app.run()