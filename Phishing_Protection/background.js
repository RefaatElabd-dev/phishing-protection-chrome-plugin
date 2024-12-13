chrome.runtime.onInstalled.addListener(() => {
    updateRulesFromAPI();
});

function updateRulesFromAPI() {
    const apiEndpoint = 'http://localhost:5000/blocklist'; // Adjust to match your Flask server's URL

    // Fetch blocklist from the API
    fetch(apiEndpoint)
        .then(response => response.json())
        .then(data => {
            const blocklist = data.blocklist || [];
            const rules = blocklist.map(entry => ({
                id: entry.id,
                priority: 1,
                action: { type: "block" },
                condition: {
                    urlFilter: entry.url,
                    resourceTypes: ["main_frame", "sub_frame"]
                }
            }));

            // Update declarativeNetRequest rules
            chrome.declarativeNetRequest.updateDynamicRules({
                removeRuleIds: blocklist.map(entry => entry.id),
                addRules: rules
            }, () => {
                console.log('Updated plugin rules from API.');
            });
        })
        .catch(error => console.error('Failed to fetch blocklist from API:', error));
}

// Periodically refresh rules
setInterval(updateRulesFromAPI, 60000); // Refresh every 60 seconds
