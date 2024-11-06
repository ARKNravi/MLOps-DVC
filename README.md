**Dokumentasi: Demonstrasi Data Versioning menggunakan DVC**

### Kasus ML Sederhana: Prediksi Kualitas Wine

Dalam kasus ini, kita akan menggunakan dataset "Wine Quality" dari [UCI Machine Learning Repository](https://archive.ics.uci.edu/ml/machine-learning-databases/wine-quality/) untuk memprediksi kualitas wine berdasarkan berbagai fitur. Model sederhana akan dilatih untuk melakukan regresi pada dataset tersebut. Selain itu, kita akan menggunakan Supabase sebagai penyimpanan untuk versioning dataset dan model dengan DVC.

### Prasyarat
1. **Instalasi Git** – DVC bekerja di atas Git, jadi pastikan Git sudah terpasang.
2. **Python dan Dependensi** – Instal Python, scikit-learn, pandas, dll.
3. **DVC** – Install DVC dengan perintah:
   ```bash
   pip install dvc
   ```
4. **Akun Supabase** – Buat akun di [Supabase](https://supabase.com/) dan buat proyek baru untuk penyimpanan.

### Langkah-langkah

#### 1. Clone Repository
- Clone repository yang sudah ada dari GitHub:
```bash
git clone https://github.com/ARKNravi/MLOps-DVC.git
cd MLOps-DVC
```

#### 2. Inisialisasi Project
- Inisialisasi DVC di dalam direktori proyek:
```bash
dvc init
```

#### 3. Mendownload Dataset
- Download dataset wine quality dari UCI dan simpan di folder `data`.
```bash
mkdir data
curl https://archive.ics.uci.edu/ml/machine-learning-databases/wine-quality/winequality-red.csv -o data/winequality-red.csv
```

#### 4. Versioning Dataset dengan DVC
- Tambahkan dataset ke dalam version control DVC:
```bash
dvc add data/winequality-red.csv
```
- Commit perubahan pada Git:
```bash
git add data/winequality-red.csv.dvc .gitignore
git commit -m "Add wine quality dataset"
```

#### 5. Konfigurasi Remote Storage di Supabase
- Buat bucket di Supabase untuk penyimpanan.
- Buat access key untuk mengakses bucket tersebut.
- Tambahkan remote storage ke DVC:
```bash
dvc remote add -d supabase-remote s3://DVC-MLOps
```
- Modifikasi endpoint dan tambahkan kredensial akses:
```bash
dvc remote modify supabase-remote endpointurl https://zyzahbhyrgrsakuwwdjr.supabase.co/storage/v1/s3
dvc remote modify supabase-remote access_key_id <supabase-access-key>
dvc remote modify supabase-remote secret_access_key <supabase-secret-key>
```
- Push dataset ke remote storage:
```bash
dvc push
```

#### 6. Menggabungkan Dataset Tambahan
- Buat file CSV baru bernama `winequality-red-additional.csv` dengan data tambahan di folder `data/`.
- Buat file `merge_data.py` untuk menggabungkan dataset lama dan dataset tambahan:
```python
import pandas as pd

# Load original dataset
data_original = pd.read_csv('data/winequality-red.csv', sep=';')

# Load additional dataset
data_additional = pd.read_csv('data/winequality-red-additional.csv', sep=';')

# Merge both datasets
data_combined = pd.concat([data_original, data_additional])

# Save combined dataset
data_combined.to_csv('data/winequality-red-combined.csv', sep=';', index=False)

print("Dataset has been successfully combined and saved.")
```
- Jalankan skrip untuk menggabungkan dataset:
```bash
python merge_data.py
```

#### 7. Membuat Model Sederhana
- Buat file `train.py` untuk melatih model sederhana dengan scikit-learn:
```python
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
import joblib

# Load dataset
data = pd.read_csv('data/winequality-red-combined.csv', sep=';')

# Split data
X = data.drop('quality', axis=1)
y = data['quality']
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train model
model = LinearRegression()
model.fit(X_train, y_train)

# Save model
joblib.dump(model, 'model/model.pkl')
```
- Jalankan skrip untuk melatih model dan menyimpan outputnya di folder `model`:
```bash
mkdir model
python train.py
```

#### 8. Versioning Model dengan DVC
- Tambahkan model yang dilatih ke dalam DVC:
```bash
dvc add model/model.pkl
```
- Commit perubahan ke Git:
```bash
git add model/model.pkl.dvc
git commit -m "Add trained model"
```

#### 9. Pushing Model ke Remote
- Push model yang telah dilatih ke remote storage di Supabase:
```bash
dvc push
```

#### 10. Menggunakan DVC untuk Reproduksi dan Versioning
- Buat file `dvc.yaml` untuk mendefinisikan pipeline:
```yaml
stages:
  merge:
    cmd: python merge_data.py
    deps:
      - data/winequality-red.csv
      - data/winequality-red-additional.csv
    outs:
      - data/winequality-red-combined.csv

  train:
    cmd: python train.py
    deps:
      - data/winequality-red-combined.csv
      - train.py
    outs:
      - model/model.pkl
```
- Commit `dvc.yaml` ke Git:
```bash
git add dvc.yaml
```
- Jalankan pipeline untuk memastikan semuanya up-to-date:
```bash
dvc repro
```
- Jika ada perubahan data atau model, jalankan perintah berikut untuk mereproduksi pipeline:
```bash
dvc repro
dvc push
```

#### 11. Bukti DVC Berhasil Dijalankan
Contoh output saat menjalankan perintah `dvc repro` dan `dvc push` untuk membuktikan bahwa DVC berhasil dijalankan:
```bash
$ dvc repro
'data\winequality-red.csv.dvc' didn't change, skipping
Running stage 'merge':
> python merge_data.py
Dataset has been successfully combined and saved.
Updating lock file 'dvc.lock'

Running stage 'train':
> python train.py
Updating lock file 'dvc.lock'

To track the changes with git, run:

        git add dvc.lock

To enable auto staging, run:

        dvc config core.autostage true

Use `dvc push` to send your updates to remote storage.
```

Setelah itu, lakukan push ke remote:
```bash
$ dvc push
Collecting
Pushing
2 files pushed
```
Output tersebut menunjukkan bahwa pipeline berhasil dijalankan dan model telah diperbarui, lalu data dan model yang baru berhasil diunggah ke remote storage.

### Revert ke Versi Sebelumnya
- **Melihat Riwayat Commit**: Gunakan perintah `git log` untuk melihat riwayat commit.
- **Checkout ke Commit Lama**: Gunakan perintah `git checkout <commit-hash>` untuk kembali ke versi sebelumnya.
- **DVC Checkout**: Setelah checkout, gunakan `dvc checkout` untuk mengembalikan dataset dan model ke versi tersebut.
```bash
dvc checkout
```
- **Membuat Branch Baru (Opsional)**: Jika ingin bekerja dengan versi lama tanpa mempengaruhi branch utama:
```bash
git switch -c revert-to-old-model
```

### Kesimpulan
Dalam demonstrasi ini, Anda belajar:
1. **Versioning Dataset dan Model** dengan DVC.
2. **Mengelola Remote Storage** menggunakan Supabase.
3. **Reproduksi Otomatis** dari model dan dataset dengan menggunakan pipeline `dvc.yaml`.
4. **Revert ke Versi Sebelumnya** menggunakan Git dan DVC.
5. **Menggabungkan Dataset Tambahan** untuk memperbarui dan melatih ulang model.
6. **Bukti Keberhasilan** dengan menunjukkan output dari DVC saat pipeline dijalankan.

Dengan DVC, pengelolaan dataset dan model menjadi lebih efisien, reproducible, dan mudah untuk dikerjakan secara kolaboratif.

