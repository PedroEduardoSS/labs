import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest

# 1. Inserindo Logs

# Caso tenha logs em um csv
# df = pd.read_csv("my_logs.csv")
# print(df.head())

# Caso tenha logs em um txt
# with open("my_logs.txt") as f:
#     raw_logs = f.readlines()

logs = [
    "2025-03-06 08:00:00, INFO, User login success, user: admin",
    "2025-03-06 08:01:23, INFO, User login success, user: peter",
    "2025-03-06 08:02:45, ERROR, Failed login attempt, user: peter",
]
parsed_logs = []
for line in logs:
    parts = [p.strip() for p in line.split(",")]
    timestamp = parts[0]
    level = parts[1]
    message = parts[2]
    user = parts[3].split(":")[1].strip() if "user:" in parts[3] else None
    parsed_logs.append({"timestamp": timestamp, "level": level, "message": message, "user": user})

# Converter para DataFrame
df_logs = pd.DataFrame(parsed_logs)
print(df_logs.head())

# 2. Pré-processamento e Extração

# Simule 50 minutos de tentativas normais de login (cerca de 5 por minuto, em média).
np.random.seed(42)
normal_counts = np.random.poisson(lam=5, size=50)

# Simular anomalia: um pico nas tentativas de login (por exemplo, um invasor tenta mais de 30 vezes em um minuto).
anomalous_counts = np.array([30, 40, 50])

# Combine os dados
login_attempts = np.concatenate([normal_counts, anomalous_counts])
print("Login attempts per minute:", login_attempts)

# 3. Implementando um Modelo de IA

# Prepare os dados no formato esperado pelo modelo (amostras, características).
X = login_attempts.reshape(-1, 1)

# Inicializar o modelo Isolation Forest
model = IsolationForest(contamination=0.05, random_state=42)
# Contaminação = 0,05 significa que esperamos que cerca de 5% dos dados sejam anomalias.

# Treinar o modelo
model.fit(X)

# Testando o modelo

labels = model.predict(X)
# O modelo retorna +1 para pontos normais e -1 para anomalias.

# Extraia os índices e valores de anomalia.
anomaly_indices = np.where(labels == -1)[0]
anomaly_values = login_attempts[anomaly_indices]

print("Anomaly indices:", anomaly_indices)
print("Anomaly values (login attempts):", anomaly_values)
