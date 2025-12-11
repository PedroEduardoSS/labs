from zxcvbn import zxcvbn
import bcrypt

def check_strength(password):
    result = zxcvbn(password)
    score = result["score"]
    if score == 3:
        response = "Forte suficiente: score 3"
    if score == 4:
        response = "Senha muito forte: score 4"
    else:
        feedback = result.get("feedback")
        warning = feedback.get("warning")
        suggestions = feedback.get("suggestions")
        response = f"Senha fraca: Score {score}"
        response += "\nAtenção: " + warning
        response += "\nSugestões: "
        for suggestion in suggestions:
            response += " " + suggestion
    return response

def hash_pw(password):
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode(), salt)
    return hashed
    
def verify_pw(password, hashed):
    if bcrypt.checkpw(password.encode(), hashed):
        return "Senha correta"
    else:
        return "Senha incorreta"
