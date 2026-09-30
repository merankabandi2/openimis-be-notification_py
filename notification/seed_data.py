DEFAULT_CHANNELS_ALL = {"in_app": True, "email": True, "sms": False}
DEFAULT_CHANNELS_IN_APP_ONLY = {"in_app": True, "email": False, "sms": False}

EVENT_TYPES = [
    ("payroll.pending_approval", "payment", DEFAULT_CHANNELS_ALL),
    ("payroll.approved", "payment", DEFAULT_CHANNELS_ALL),
    ("payroll.rejected", "payment", DEFAULT_CHANNELS_ALL),
    ("payroll.reconciled", "payment", DEFAULT_CHANNELS_ALL),
    ("payroll.reconciliation_failed", "payment", DEFAULT_CHANNELS_ALL),
    ("activity.submitted", "activity", DEFAULT_CHANNELS_IN_APP_ONLY),
    ("activity.validated", "activity", DEFAULT_CHANNELS_ALL),
    ("activity.rejected", "activity", DEFAULT_CHANNELS_ALL),
    ("grievance.created", "grievance", DEFAULT_CHANNELS_ALL),
    ("grievance.assigned", "grievance", DEFAULT_CHANNELS_ALL),
    ("grievance.comment", "grievance", DEFAULT_CHANNELS_IN_APP_ONLY),
    ("grievance.status_changed", "grievance", DEFAULT_CHANNELS_ALL),
    ("grievance.reopened", "grievance", DEFAULT_CHANNELS_ALL),
    ("selection.quota_completed", "selection", DEFAULT_CHANNELS_ALL),
    ("selection.validation_completed", "selection", DEFAULT_CHANNELS_ALL),
    ("selection.promotion_completed", "selection", DEFAULT_CHANNELS_ALL),
    ("task.assigned", "task", DEFAULT_CHANNELS_ALL),
    ("task.completed", "task", DEFAULT_CHANNELS_ALL),
    ("task.failed", "task", DEFAULT_CHANNELS_ALL),
    ("report.snapshot_ready", "report", DEFAULT_CHANNELS_IN_APP_ONLY),
]

# (subject, body, sms_body). A grievance message names the ticket by its number
# only; the e-mail links to the ticket. sms_body is written without accents: a character outside
# the GSM 7-bit alphabet switches an SMS to UCS-2, 70 characters per message.
FRENCH_TEMPLATES = {
    "payroll.pending_approval": (
        "Payroll en attente d'approbation",
        "Le payroll {payroll_name} pour le point de paiement {payment_point} est en attente de votre approbation.",
        "Payroll {payroll_name} en attente d'approbation.",
    ),
    "payroll.approved": (
        "Payroll approuvé",
        "Le payroll {payroll_name} a été approuvé par {actor_name}.",
        "Payroll {payroll_name} approuve.",
    ),
    "payroll.rejected": (
        "Payroll rejeté",
        "Le payroll {payroll_name} a été rejeté par {actor_name}.",
        "Payroll {payroll_name} rejete.",
    ),
    "payroll.reconciled": (
        "Payroll réconcilié",
        "Le payroll {payroll_name} a été réconcilié avec succès.",
        "Payroll {payroll_name} reconcilie.",
    ),
    "payroll.reconciliation_failed": (
        "Échec de réconciliation",
        "La réconciliation du payroll {payroll_name} a échoué. Statut : {status}.",
        "Echec reconciliation {payroll_name}.",
    ),
    "activity.submitted": (
        "Activité soumise pour validation",
        "Une activité {activity_type} à {location} du {date} est en attente de validation.",
        "Activite {activity_type} a valider.",
    ),
    "activity.validated": (
        "Activité validée",
        "L'activité {activity_type} à {location} a été validée par {actor_name}.",
        "Activite {activity_type} validee.",
    ),
    "activity.rejected": (
        "Activité rejetée",
        "L'activité {activity_type} à {location} a été rejetée par {actor_name}. Motif : {comment}.",
        "Activite {activity_type} rejetee: {comment}.",
    ),
    "grievance.created": (
        "Nouvelle plainte",
        "Une nouvelle plainte #{ticket_number} a été enregistrée.",
        "Nouvelle plainte #{ticket_number}.",
    ),
    "grievance.assigned": (
        "Plainte assignée",
        "La plainte #{ticket_number} vous a été assignée.",
        "Plainte #{ticket_number} vous est assignee.",
    ),
    "grievance.comment": (
        "Nouveau commentaire",
        "Un commentaire a été ajouté à la plainte #{ticket_number}.",
        "Commentaire sur plainte #{ticket_number}.",
    ),
    "grievance.status_changed": (
        "Changement de statut",
        "Le statut de la plainte #{ticket_number} a changé.",
        "Plainte #{ticket_number}: statut modifie.",
    ),
    "grievance.reopened": (
        "Plainte rouverte",
        "La plainte #{ticket_number} a été rouverte.",
        "Plainte #{ticket_number} reouverte.",
    ),
    "selection.quota_completed": (
        "Sélection par quota terminée",
        "La sélection par quota pour le programme {program_name}, round {round}, est terminée. {selected_count} ménages sélectionnés.",
        "Selection quota terminee: {selected_count} menages.",
    ),
    "selection.validation_completed": (
        "Validation communautaire terminée",
        "La validation communautaire pour {program_name} à {location} est terminée. {validated_count} validés, {rejected_count} rejetés.",
        "Validation communautaire terminee a {location}.",
    ),
    "selection.promotion_completed": (
        "Promotion en bénéficiaires terminée",
        "{promoted_count} ménages ont été promus en bénéficiaires pour {program_name}.",
        "{promoted_count} menages promus beneficiaires.",
    ),
    "task.assigned": (
        "Tâche assignée",
        "Une tâche requiert votre action : {task_description}.",
        "Tache assignee: {task_description}.",
    ),
    "task.completed": (
        "Tâche terminée",
        "La tâche {task_description} a été terminée par {actor_name}.",
        "Tache completee: {task_description}.",
    ),
    "task.failed": (
        "Tâche échouée",
        "La tâche {task_description} a échoué. {reason}.",
        "Tache echouee: {task_description}.",
    ),
    "report.snapshot_ready": (
        "Cadre de résultats prêt",
        "Le cadre de résultats \"{snapshot_name}\" est prêt. Cliquez pour télécharger.",
        "",
    ),
}
