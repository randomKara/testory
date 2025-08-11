#!/bin/bash

echo "🧪 Test des utilisateurs Kratos"
echo "==============================="

# Vérifier que Kratos Admin est disponible
echo "1. Vérification de l'API Admin Kratos..."
if curl -s http://localhost:4434/admin/health/ready > /dev/null; then
    echo "✅ Kratos Admin API disponible"
else
    echo "❌ Kratos Admin API non disponible"
    exit 1
fi

# Lister les utilisateurs
echo ""
echo "2. Liste des utilisateurs créés :"
curl -s http://localhost:4434/admin/identities | jq '.[] | {id: .id, email: .traits.email, state: .state}' 2>/dev/null || echo "❌ Erreur lors de la récupération des utilisateurs"

# Tester la redirection de l'application
echo ""
echo "3. Test de la redirection automatique :"
RESPONSE=$(curl -s -w "%{http_code}" http://localhost:5000/ -o /dev/null)
if [ "$RESPONSE" = "302" ]; then
    echo "✅ Redirection automatique fonctionne (HTTP 302)"
else
    echo "❌ Redirection automatique ne fonctionne pas (HTTP $RESPONSE)"
fi

# Tester la redirection vers Kratos UI
echo ""
echo "4. Test de la redirection vers Kratos UI :"
LOCATION=$(curl -s -D - http://localhost:5000/login | grep -i location | cut -d' ' -f2 | tr -d '\r')
if [[ "$LOCATION" == *"4455"* ]]; then
    echo "✅ Redirection vers Kratos UI fonctionne"
else
    echo "❌ Redirection vers Kratos UI incorrecte: $LOCATION"
fi

echo ""
echo "5. Vérification des services :"
docker compose ps --format "table {{.Name}}\t{{.Status}}\t{{.Ports}}"

echo ""
echo "🎯 Pour tester manuellement :"
echo "   Aller sur http://localhost:5000"
echo "   Utiliser : user1@example.com / user1"
echo "   Ou       : user2@example.com / user2"
