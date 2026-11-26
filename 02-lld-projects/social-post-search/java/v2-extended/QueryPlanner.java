package v2_extended;

import java.util.*;

public class QueryPlanner {
    private final InvertedIndex index;

    public QueryPlanner(InvertedIndex index) {
        this.index = index;
    }

    public List<String> planAndExecute(String rawQuery) {
        if (rawQuery == null || rawQuery.trim().isEmpty()) return new ArrayList<>();
        
        String[] tokens = rawQuery.split("\\s+");
        List<List<String>> orGroups = new ArrayList<>();
        List<String> currentAndGroup = new ArrayList<>();

        for (String token : tokens) {
            if (token.equalsIgnoreCase("OR")) {
                if (!currentAndGroup.isEmpty()) {
                    orGroups.add(new ArrayList<>(currentAndGroup));
                    currentAndGroup.clear();
                }
            } else if (token.equalsIgnoreCase("AND")) {
                continue;
            } else {
                List<String> filtered = Tokenizer.tokenize(token);
                if (!filtered.isEmpty()) {
                    currentAndGroup.addAll(filtered);
                }
            }
        }

        if (!currentAndGroup.isEmpty()) {
            orGroups.add(currentAndGroup);
        }

        Set<String> finalSet = new HashSet<>();
        for (List<String> group : orGroups) {
            Set<String> groupSet = null;
            for (String term : group) {
                Set<String> termSet = index.getIndex().getOrDefault(term, Collections.emptySet());
                if (groupSet == null) {
                    groupSet = new HashSet<>(termSet);
                } else {
                    groupSet.retainAll(termSet);
                }
            }
            if (groupSet != null) {
                finalSet.addAll(groupSet);
            }
        }

        return new ArrayList<>(finalSet);
    }
}
