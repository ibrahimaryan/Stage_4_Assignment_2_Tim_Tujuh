from pymongo import MongoClient

# Koneksi ke MongoDB
client = MongoClient(
    "mongodb+srv://timtujuh:vV2WEXiqjSTmPevl@clustertimtujuh.8p34h.mongodb.net/?retryWrites=true&w=majority&appName=ClusterTimTujuh"
)

# Akses database dan collection
db = client["TimTujuhDatabase"]
collection = db["MySensorData"]

# Hapus semua data (dokumen) dalam collection
result = collection.delete_many({})

# Cetak jumlah dokumen yang dihapus
print(f"{result.deleted_count} dokumen telah dihapus.")