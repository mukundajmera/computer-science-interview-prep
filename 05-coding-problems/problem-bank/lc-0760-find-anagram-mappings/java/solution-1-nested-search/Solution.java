class Solution {
    public int[] anagramMappings(int[] nums1, int[] nums2) {
        int[] result = new int[nums1.length];
        boolean[] used = new boolean[nums2.length];
        for (int i = 0; i < nums1.length; i++) {
            for (int j = 0; j < nums2.length; j++) {
                if (!used[j] && nums2[j] == nums1[i]) {
                    used[j] = true;
                    result[i] = j;
                    break;
                }
            }
        }
        return result;
    }
}
