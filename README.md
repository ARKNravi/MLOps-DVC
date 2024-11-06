**Dokumentasi: Demonstrasi Data Versioning menggunakan DVC**

### Kasus ML Sederhana: Prediksi Kualitas Wine

Dalam kasus ini, kita akan menggunakan dataset "Wine Quality" dari [UCI Machine Learning Repository](https://archive.ics.uci.edu/ml/machine-learning-databases/wine-quality/) untuk memprediksi kualitas wine berdasarkan berbagai fitur. Model sederhana akan dilatih untuk melakukan regresi pada dataset tersebut. Selain itu, kita akan menggunakan Supabase sebagai penyimpanan untuk versioning dataset dan model dengan DVC.

### Prasyarat
1. **Instalasi Git** – DVC bekerja di atas Git, jadi pastikan Git sudah terpasang.
2. **Python dan Dependensi** – Instal Python, scikit-learn, pandas, dll.
3. **Akun Supabase** – Buat akun di [Supabase](https://supabase.com/) dan buat proyek baru untuk penyimpanan.

### Langkah-langkah

#### 1. Buat Project Directory
- Buat direktori proyek baru dan pindah ke direktori tersebut:
```bash
mkdir wine-quality-dvc
cd wine-quality-dvc
```

#### 2. Buat File Requirements
- Buat file `requirements.txt` untuk mencatat dependensi yang diperlukan oleh proyek ini:
```text
pandas
scikit-learn
joblib
dvc
# Untuk dukungan S3 dengan DVC
dvc[s3]
```
- Install semua dependensi menggunakan pip:
```bash
pip install -r requirements.txt
```

#### 3. Inisialisasi Project
- Inisialisasi Git dan DVC di dalam direktori proyek:
```bash
git init
dvc init
```

#### 4. Mendownload Dataset
- Download dataset wine quality dari UCI dan simpan di folder `data`.
```bash
mkdir data
curl https://archive.ics.uci.edu/ml/machine-learning-databases/wine-quality/winequality-red.csv -o data/winequality-red.csv
```

#### 5. Versioning Dataset dengan DVC
- Tambahkan dataset ke dalam version control DVC:
```bash
dvc add data/winequality-red.csv
```
- Commit perubahan pada Git:
```bash
git add data/winequality-red.csv.dvc .gitignore
```
```bash
git commit -m "Add wine quality dataset"
```

#### 6. Konfigurasi Remote Storage di Supabase
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

#### 7. Menggabungkan Dataset Tambahan
- Jika file `winequality-red-additional.csv` tidak ada, skrip akan membuat file tersebut secara otomatis dengan beberapa data tambahan.
- Jika file `winequality-red-combined.csv` tidak ada, skrip berikut akan membuatnya secara otomatis.
- Buat file `merge_data.py` untuk menggabungkan dataset lama dan dataset tambahan:
```python
import os
import pandas as pd

# Load original dataset
data_original = pd.read_csv('data/winequality-red.csv', sep=';')

# Check if additional dataset exists or create it
additional_file_path = 'data/winequality-red-additional.csv'
if not os.path.exists(additional_file_path):
    # Create a sample additional dataset if it doesn't exist
    os.makedirs(os.path.dirname(additional_file_path), exist_ok=True)
    data_additional = data_original.sample(5, random_state=42)  # Create 5 sample rows for additional data
    data_additional.to_csv(additional_file_path, sep=';', index=False)
else:
    data_additional = pd.read_csv(additional_file_path, sep=';')

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

#### 8. Membuat Model Sederhana
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

#### 9. Versioning Model dengan DVC
- Tambahkan model yang dilatih ke dalam DVC:
```bash
dvc add model/model.pkl
```
- Commit perubahan ke Git:
```bash
git add model/model.pkl.dvc
```
```bash
git commit -m "Add trained model"
```

#### 10. Pushing Model ke Remote
- Push model yang telah dilatih ke remote storage di Supabase:
```bash
dvc push
```

#### 11. Menggunakan DVC untuk Reproduksi dan Versioning
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
```bash
git commit -m "Add DVC pipeline"
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

#### 12. Bukti DVC Berhasil Dijalankan
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
```bash
git checkout b670ca29fc89f700c4e8989c423fc8299162c075
```
- **DVC Checkout**: Setelah checkout, gunakan `dvc checkout` untuk mengembalikan dataset dan model ke versi tersebut.
```bash
dvc checkout
```

#### Bukti Revert Berhasil Dijalankan
Contoh output saat melakukan revert ke commit sebelumnya:
```bash
rkunt@MSI MINGW64 /c/Recovery/Project/MLOpsSemester5/MLOps-DVC/wine-quality-dvc (main)
$ git checkout b670ca29fc89f700c4e8989c423fc8299162c075
Note: switching to 'b670ca29fc89f700c4e8989c423fc8299162c075'.

You are in 'detached HEAD' state. You can look around, make experimental
changes and commit them, and you can discard any commits you make in this
state without impacting any branches by switching back to a branch.

HEAD is now at b670ca2 Create README.md
M       dvc.lock

$ dvc repro
'data\winequality-red.csv.dvc' didn't change, skipping
Running stage 'merge':
> python merge-data.py
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

$ dvc push
Collecting
Pushing
2 files pushed

$ dvc checkout
Building workspace index
Comparing indexes
Applying changes
```
Output ini menunjukkan bahwa revert berhasil dilakukan dan pipeline diperbarui.

### Kesimpulan
Dalam demonstrasi ini, Anda belajar:
1. **Versioning Dataset dan Model** dengan DVC.
2. **Mengelola Remote Storage** menggunakan Supabase.
3. **Reproduksi Otomatis** dari model dan dataset dengan menggunakan pipeline `dvc.yaml`.
4. **Revert ke Versi Sebelumnya** menggunakan Git dan DVC, beserta bukti keberhasilan revert.
5. **Menggabungkan Dataset Tambahan** untuk memperbarui dan melatih ulang model.
6. **Bukti Keberhasilan** dengan menunjukkan output dari DVC saat pipeline dijalankan.

Dengan DVC, pengelolaan dataset dan model menjadi lebih efisien, reproducible, dan mudah untuk dikerjakan secara kolaboratif.

### Screenshot Bukti
Tambahkan screenshot dari output untuk memperkuat bukti bahwa semua langkah telah berhasil dijalankan.

