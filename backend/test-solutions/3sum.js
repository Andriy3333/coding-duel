class Solution {
    threeSum(nums) {
        nums.sort((a, b) => a - b);
        const result = [];
        
        for (let i = 0; i < nums.length - 2; i++) {
            // Skip duplicates for the first element
            if (i > 0 && nums[i] === nums[i - 1]) {
                continue;
            }
            
            let left = i + 1, right = nums.length - 1;
            
            while (left < right) {
                const currentSum = nums[i] + nums[left] + nums[right];
                
                if (currentSum === 0) {
                    result.push([nums[i], nums[left], nums[right]]);
                    
                    // Skip duplicates for left and right pointers
                    while (left < right && nums[left] === nums[left + 1]) {
                        left++;
                    }
                    while (left < right && nums[right] === nums[right - 1]) {
                        right--;
                    }
                    
                    left++;
                    right--;
                } else if (currentSum < 0) {
                    left++;
                } else {
                    right--;
                }
            }
        }
        
        return result;
    }
}