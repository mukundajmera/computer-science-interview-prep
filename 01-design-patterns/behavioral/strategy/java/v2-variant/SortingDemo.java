/**
 * Strategy Pattern - V2 Variant: Sorting Algorithms
 */

import java.util.Arrays;

// Strategy Interface
interface SortStrategy {
    int[] sort(int[] data);
    String getName();
}

// Concrete Strategies
class BubbleSort implements SortStrategy {
    @Override
    public int[] sort(int[] data) {
        int[] arr = data.clone();
        int n = arr.length;
        for (int i = 0; i < n - 1; i++) {
            for (int j = 0; j < n - i - 1; j++) {
                if (arr[j] > arr[j + 1]) {
                    int temp = arr[j];
                    arr[j] = arr[j + 1];
                    arr[j + 1] = temp;
                }
            }
        }
        return arr;
    }
    
    @Override
    public String getName() { return "Bubble Sort"; }
}

class QuickSort implements SortStrategy {
    @Override
    public int[] sort(int[] data) {
        int[] arr = data.clone();
        quickSort(arr, 0, arr.length - 1);
        return arr;
    }
    
    private void quickSort(int[] arr, int low, int high) {
        if (low < high) {
            int pi = partition(arr, low, high);
            quickSort(arr, low, pi - 1);
            quickSort(arr, pi + 1, high);
        }
    }
    
    private int partition(int[] arr, int low, int high) {
        int pivot = arr[high];
        int i = low - 1;
        for (int j = low; j < high; j++) {
            if (arr[j] < pivot) {
                i++;
                int temp = arr[i];
                arr[i] = arr[j];
                arr[j] = temp;
            }
        }
        int temp = arr[i + 1];
        arr[i + 1] = arr[high];
        arr[high] = temp;
        return i + 1;
    }
    
    @Override
    public String getName() { return "Quick Sort"; }
}

class MergeSort implements SortStrategy {
    @Override
    public int[] sort(int[] data) {
        int[] arr = data.clone();
        mergeSort(arr, 0, arr.length - 1);
        return arr;
    }
    
    private void mergeSort(int[] arr, int left, int right) {
        if (left < right) {
            int mid = (left + right) / 2;
            mergeSort(arr, left, mid);
            mergeSort(arr, mid + 1, right);
            merge(arr, left, mid, right);
        }
    }
    
    private void merge(int[] arr, int left, int mid, int right) {
        int[] temp = new int[right - left + 1];
        int i = left, j = mid + 1, k = 0;
        
        while (i <= mid && j <= right) {
            temp[k++] = arr[i] <= arr[j] ? arr[i++] : arr[j++];
        }
        while (i <= mid) temp[k++] = arr[i++];
        while (j <= right) temp[k++] = arr[j++];
        
        System.arraycopy(temp, 0, arr, left, temp.length);
    }
    
    @Override
    public String getName() { return "Merge Sort"; }
}

// Context with automatic strategy selection
class SmartSorter {
    private SortStrategy strategy;
    
    public void setStrategy(SortStrategy strategy) {
        this.strategy = strategy;
    }
    
    // Auto-select based on data size
    public void autoSelectStrategy(int dataSize) {
        if (dataSize < 10) {
            strategy = new BubbleSort();  // Simple for small data
        } else if (dataSize < 1000) {
            strategy = new QuickSort();   // Fast for medium data
        } else {
            strategy = new MergeSort();   // Stable for large data
        }
        System.out.println("Auto-selected: " + strategy.getName());
    }
    
    public int[] sort(int[] data) {
        if (strategy == null) {
            autoSelectStrategy(data.length);
        }
        long start = System.nanoTime();
        int[] result = strategy.sort(data);
        long elapsed = System.nanoTime() - start;
        System.out.printf("%s took %.3f ms%n", strategy.getName(), elapsed / 1_000_000.0);
        return result;
    }
}

public class SortingDemo {
    public static void main(String[] args) {
        SmartSorter sorter = new SmartSorter();
        int[] testData = {64, 34, 25, 12, 22, 11, 90, 5, 77, 30};
        
        System.out.println("Original: " + Arrays.toString(testData));
        System.out.println();
        
        // Manual strategy selection
        sorter.setStrategy(new BubbleSort());
        System.out.println("Result: " + Arrays.toString(sorter.sort(testData)));
        
        sorter.setStrategy(new QuickSort());
        System.out.println("Result: " + Arrays.toString(sorter.sort(testData)));
        
        sorter.setStrategy(new MergeSort());
        System.out.println("Result: " + Arrays.toString(sorter.sort(testData)));
        
        // Auto-selection
        System.out.println("\n=== Auto-Selection ===");
        SmartSorter auto = new SmartSorter();
        auto.sort(new int[5]);      // Will use BubbleSort
        auto.autoSelectStrategy(500);  // Will use QuickSort
        auto.autoSelectStrategy(5000); // Will use MergeSort
    }
}
