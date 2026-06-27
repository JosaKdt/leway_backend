import smtplib
import secrets
import string
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.core.config import settings


def _send_email(to: str, subject: str, html: str) -> bool:
    """Envoie un email via Gmail SMTP."""
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"]    = f"ORIAB <{settings.GMAIL_USER}>"
        msg["To"]      = to

        msg.attach(MIMEText(html, "html"))

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(settings.GMAIL_USER, settings.GMAIL_APP_PASSWORD)
            server.sendmail(settings.GMAIL_USER, to, msg.as_string())

        return True
    except Exception as e:
        print(f"[EMAIL] Erreur envoi : {e}")
        return False


def generate_temp_password(length: int = 12) -> str:
    """Génère un mot de passe temporaire sécurisé."""
    alphabet = string.ascii_letters + string.digits + "!@#$%"
    return ''.join(secrets.choice(alphabet) for _ in range(length))


def send_invitation_representant(
    nom: str,
    prenom: str,
    email: str,
    nom_universite: str,
    mot_de_passe_temp: str,
) -> bool:
    """Envoie l'email d'invitation à un nouveau représentant d'université."""
    html = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
        <div style="background-color: #00853F; padding: 24px; border-radius: 8px 8px 0 0;">
            <h1 style="color: white; margin: 0; font-size: 24px;">ORIAB</h1>
            <p style="color: rgba(255,255,255,0.8); margin: 4px 0 0 0; font-size: 14px;">
                Orientation des Bacheliers au Bénin
            </p>
        </div>
        <div style="background-color: #f9fafb; padding: 32px; border-radius: 0 0 8px 8px; border: 1px solid #e5e7eb;">
            <p style="color: #374151; font-size: 16px;">Bonjour <strong>{prenom} {nom}</strong>,</p>
            <p style="color: #6b7280; font-size: 14px; line-height: 1.6;">
                Vous avez été invité(e) à gérer le profil de <strong>{nom_universite}</strong>
                sur la plateforme ORIAB.
            </p>
            <div style="background-color: white; border: 1px solid #e5e7eb; border-radius: 8px; padding: 20px; margin: 24px 0;">
                <p style="color: #374151; font-weight: bold; margin: 0 0 12px 0;">
                    Vos identifiants de connexion :
                </p>
                <p style="margin: 6px 0; color: #6b7280; font-size: 14px;">
                    <strong>Email :</strong> {email}
                </p>
                <p style="margin: 6px 0; color: #6b7280; font-size: 14px;">
                    <strong>Mot de passe temporaire :</strong>
                    <span style="background-color: #f3f4f6; padding: 2px 8px; border-radius: 4px;
                                 font-family: monospace; font-size: 15px; color: #111827;">
                        {mot_de_passe_temp}
                    </span>
                </p>
            </div>
            <p style="color: #6b7280; font-size: 13px;">
                ⚠️ Ce mot de passe est temporaire. Changez-le dès votre première connexion.
            </p>
            <p style="color: #9ca3af; font-size: 12px; text-align: center; margin-top: 24px;">
                L'équipe ORIAB — Plateforme d'orientation post-baccalauréat au Bénin
            </p>
        </div>
    </div>
    """
    return _send_email(
        to=email,
        subject=f"Votre accès ORIAB — Espace Université {nom_universite}",
        html=html,
    )


def send_otp_bachelier(email: str, prenom: str, code: str) -> bool:
    """Envoie le code OTP de vérification au bachelier."""
    html = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
        <div style="background-color: #00853F; padding: 24px; border-radius: 8px 8px 0 0;">
            <h1 style="color: white; margin: 0; font-size: 24px;">ORIAB</h1>
            <p style="color: rgba(255,255,255,0.8); margin: 4px 0 0 0; font-size: 14px;">
                Orientation des Bacheliers au Bénin
            </p>
        </div>
        <div style="background-color: #f9fafb; padding: 32px; border-radius: 0 0 8px 8px; border: 1px solid #e5e7eb;">
            <p style="color: #374151; font-size: 16px;">Bonjour <strong>{prenom}</strong>,</p>
            <p style="color: #6b7280; font-size: 14px; line-height: 1.6;">
                Voici votre code de vérification pour activer votre compte ORIAB :
            </p>
            <div style="text-align: center; margin: 32px 0;">
                <span style="background-color: #f3f4f6; border: 2px dashed #00853F;
                             padding: 16px 32px; border-radius: 8px;
                             font-family: monospace; font-size: 32px;
                             font-weight: bold; color: #111827; letter-spacing: 8px;">
                    {code}
                </span>
            </div>
            <p style="color: #ef4444; font-size: 13px; text-align: center;">
                ⚠️ Ce code expire dans <strong>10 minutes</strong>.
            </p>
            <p style="color: #6b7280; font-size: 13px; text-align: center; margin-top: 16px;">
                Si vous n'avez pas créé de compte ORIAB, ignorez cet email.
            </p>
            <p style="color: #9ca3af; font-size: 12px; text-align: center; margin-top: 24px;">
                L'équipe ORIAB — Plateforme d'orientation post-baccalauréat au Bénin
            </p>
        </div>
    </div>
    """
    return _send_email(
        to=email,
        subject="Votre code de vérification ORIAB",
        html=html,
    )

def send_demande_representant_validee(
    nom: str,
    prenom: str,
    email: str,
    nom_universite: str,
) -> bool:
    """Notifie un demandeur que sa demande de représentant a été acceptée."""
    html = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
        <div style="background-color: #00853F; padding: 24px; border-radius: 8px 8px 0 0;">
            <h1 style="color: white; margin: 0; font-size: 24px;">ORIAB</h1>
            <p style="color: rgba(255,255,255,0.8); margin: 4px 0 0 0; font-size: 14px;">
                Orientation des Bacheliers au Bénin
            </p>
        </div>
        <div style="background-color: #f9fafb; padding: 32px; border-radius: 0 0 8px 8px; border: 1px solid #e5e7eb;">
            <p style="color: #374151; font-size: 16px;">Bonjour <strong>{prenom} {nom}</strong>,</p>
            <p style="color: #6b7280; font-size: 14px; line-height: 1.6;">
                Bonne nouvelle ! Votre demande pour représenter
                <strong>{nom_universite}</strong> sur la plateforme ORIAB a été
                <strong style="color: #00853F;">acceptée</strong>.
            </p>
            <p style="color: #6b7280; font-size: 14px; line-height: 1.6;">
                Vous pouvez désormais vous connecter avec l'email et le mot de passe
                que vous avez choisis lors de votre demande, et commencer à gérer le
                profil de votre établissement.
            </p>
            <p style="color: #9ca3af; font-size: 12px; text-align: center; margin-top: 24px;">
                L'équipe ORIAB — Plateforme d'orientation post-baccalauréat au Bénin
            </p>
        </div>
    </div>
    """
    return _send_email(
        to=email,
        subject=f"Votre demande ORIAB a été acceptée — {nom_universite}",
        html=html,
    )


def send_demande_representant_refusee(
    nom: str,
    prenom: str,
    email: str,
    motif: str,
) -> bool:
    """Notifie un demandeur que sa demande de représentant a été refusée."""
    html = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
        <div style="background-color: #00853F; padding: 24px; border-radius: 8px 8px 0 0;">
            <h1 style="color: white; margin: 0; font-size: 24px;">ORIAB</h1>
            <p style="color: rgba(255,255,255,0.8); margin: 4px 0 0 0; font-size: 14px;">
                Orientation des Bacheliers au Bénin
            </p>
        </div>
        <div style="background-color: #f9fafb; padding: 32px; border-radius: 0 0 8px 8px; border: 1px solid #e5e7eb;">
            <p style="color: #374151; font-size: 16px;">Bonjour <strong>{prenom} {nom}</strong>,</p>
            <p style="color: #6b7280; font-size: 14px; line-height: 1.6;">
                Nous avons examiné votre demande pour devenir représentant d'université
                sur ORIAB. Malheureusement, elle n'a pas pu être validée pour le motif
                suivant :
            </p>
            <div style="background-color: white; border-left: 4px solid #E8112D; padding: 12px 16px; margin: 20px 0;">
                <p style="color: #374151; font-size: 14px; margin: 0;">{motif}</p>
            </div>
            <p style="color: #6b7280; font-size: 14px; line-height: 1.6;">
                Vous pouvez soumettre une nouvelle demande après avoir complété votre
                dossier, ou contacter l'administration pour plus d'informations.
            </p>
            <p style="color: #9ca3af; font-size: 12px; text-align: center; margin-top: 24px;">
                L'équipe ORIAB — Plateforme d'orientation post-baccalauréat au Bénin
            </p>
        </div>
    </div>
    """
    return _send_email(
        to=email,
        subject="Suite à votre demande ORIAB",
        html=html,
    )
