import java.util.HashMap;
import java.util.List;
import java.util.Map;

class Solution {
    public double[] calcEquation(List<List<String>> equations, double[] values, List<List<String>> queries) {
        WeightedUnionFind unionFind = new WeightedUnionFind();
        for (int i = 0; i < equations.size(); i++) {
            unionFind.union(equations.get(i).get(0), equations.get(i).get(1), values[i]);
        }

        double[] answers = new double[queries.size()];
        for (int i = 0; i < queries.size(); i++) {
            answers[i] = unionFind.ratio(queries.get(i).get(0), queries.get(i).get(1));
        }
        return answers;
    }

    private static class WeightedUnionFind {
        private final Map<String, String> parent = new HashMap<>();
        private final Map<String, Double> weight = new HashMap<>();

        private void add(String item) {
            parent.putIfAbsent(item, item);
            weight.putIfAbsent(item, 1.0d);
        }

        private Root find(String item) {
            String currentParent = parent.get(item);
            if (currentParent.equals(item)) {
                return new Root(item, weight.get(item));
            }
            Root root = find(currentParent);
            parent.put(item, root.name);
            weight.put(item, weight.get(item) * root.ratio);
            return new Root(parent.get(item), weight.get(item));
        }

        private void union(String numerator, String denominator, double ratio) {
            add(numerator);
            add(denominator);
            Root numeratorRoot = find(numerator);
            Root denominatorRoot = find(denominator);
            if (numeratorRoot.name.equals(denominatorRoot.name)) {
                return;
            }
            parent.put(numeratorRoot.name, denominatorRoot.name);
            weight.put(numeratorRoot.name, ratio * denominatorRoot.ratio / numeratorRoot.ratio);
        }

        private double ratio(String numerator, String denominator) {
            if (!parent.containsKey(numerator) || !parent.containsKey(denominator)) {
                return -1.0d;
            }
            Root numeratorRoot = find(numerator);
            Root denominatorRoot = find(denominator);
            if (!numeratorRoot.name.equals(denominatorRoot.name)) {
                return -1.0d;
            }
            return numeratorRoot.ratio / denominatorRoot.ratio;
        }
    }

    private static class Root {
        private final String name;
        private final double ratio;

        private Root(String name, double ratio) {
            this.name = name;
            this.ratio = ratio;
        }
    }
}
