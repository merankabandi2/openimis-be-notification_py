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

FRENCH_TEMPLATES = {
    "payroll.pending_approval": (
        "Payroll en attente d'approbation",
        "Le payroll {payroll_name} pour le point de paiement {payment_point} est en attente de votre approbation.",
        "Payroll {payroll_name} en attente d'approbation.",
    ),
    "payroll.approved": (
        "Payroll approuve",
        "Le payroll {payroll_name} a ete approuve par {actor_name}.",
        "Payroll {payroll_name} approuve.",
    ),
    "payroll.rejected": (
        "Payroll rejete",
        "Le payroll {payroll_name} a ete rejete par {actor_name}.",
        "Payroll {payroll_name} rejete.",
    ),
    "payroll.reconciled": (
        "Payroll reconcilie",
        "Le payroll {payroll_name} a ete reconcilie avec succes.",
        "Payroll {payroll_name} reconcilie.",
    ),
    "payroll.reconciliation_failed": (
        "Echec de reconciliation",
        "La reconciliation du payroll {payroll_name} a echoue. Statut: {status}.",
        "Echec reconciliation {payroll_name}.",
    ),
    "activity.submitted": (
        "Activite soumise pour validation",
        "Une activite {activity_type} a {location} du {date} est en attente de validation.",
        "Activite {activity_type} a valider.",
    ),
    "activity.validated": (
        "Activite validee",
        "L'activite {activity_type} a {location} a ete validee par {actor_name}.",
        "Activite {activity_type} validee.",
    ),
    "activity.rejected": (
        "Activite rejetee",
        "L'activite {activity_type} a {location} a ete rejetee par {actor_name}. Motif: {comment}.",
        "Activite {activity_type} rejetee: {comment}.",
    ),
    "grievance.created": (
        "Nouvelle plainte",
        "Une nouvelle plainte #{ticket_number} a ete creee. Categorie: {category}. Priorite: {priority}.",
        "Nouvelle plainte #{ticket_number}.",
    ),
    "grievance.assigned": (
        "Plainte assignee",
        "La plainte #{ticket_number} vous a ete assignee par {actor_name}.",
        "Plainte #{ticket_number} vous est assignee.",
    ),
    "grievance.comment": (
        "Nouveau commentaire",
        "{actor_name} a commente la plainte #{ticket_number}: \"{comment_preview}\".",
        "Commentaire sur plainte #{ticket_number}.",
    ),
    "grievance.status_changed": (
        "Changement de statut",
        "La plainte #{ticket_number} est passee au statut {new_status}.",
        "Plainte #{ticket_number}: {new_status}.",
    ),
    "grievance.reopened": (
        "Plainte reouverte",
        "La plainte #{ticket_number} a ete reouverte par {actor_name}.",
        "Plainte #{ticket_number} reouverte.",
    ),
    "selection.quota_completed": (
        "Selection par quota terminee",
        "La selection par quota pour le programme {program_name}, round {round}, est terminee. {selected_count} menages selectionnes.",
        "Selection quota terminee: {selected_count} menages.",
    ),
    "selection.validation_completed": (
        "Validation communautaire terminee",
        "La validation communautaire pour {program_name} a {location} est terminee. {validated_count} valides, {rejected_count} rejetes.",
        "Validation communautaire terminee a {location}.",
    ),
    "selection.promotion_completed": (
        "Promotion en beneficiaires terminee",
        "{promoted_count} menages ont ete promus en beneficiaires pour {program_name}.",
        "{promoted_count} menages promus beneficiaires.",
    ),
    "task.assigned": (
        "Tache assignee",
        "Une tache requiert votre action: {task_description}.",
        "Tache assignee: {task_description}.",
    ),
    "task.completed": (
        "Tache completee",
        "La tache {task_description} a ete completee par {actor_name}.",
        "Tache completee: {task_description}.",
    ),
    "task.failed": (
        "Tache echouee",
        "La tache {task_description} a echoue. {reason}.",
        "Tache echouee: {task_description}.",
    ),
    "report.snapshot_ready": (
        "Cadre de résultats prêt",
        "Le cadre de résultats \"{snapshot_name}\" est prêt. Cliquez pour télécharger.",
        "",
    ),
}
