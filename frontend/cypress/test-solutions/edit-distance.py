class Solution:
    def minDistance(self, word1: str, word2: str) -> int:
        m, n = len(word1), len(word2)

        # Create DP table
        dp = [[0] * (n + 1) for _ in range(m + 1)]

        # Initialize base cases
        for i in range(m + 1):
            dp[i][0] = i  # Delete all characters from word1
        for j in range(n + 1):
            dp[0][j] = j  # Insert all characters to reach word2

        # Fill DP table
        for i in range(1, m + 1):
            for j in range(1, n + 1):
                if word1[i - 1] == word2[j - 1]:
                    # Characters match, no operation needed
                    dp[i][j] = dp[i - 1][j - 1]
                else:
                    # Take minimum of insert, delete, replace
                    dp[i][j] = 1 + min(
                        dp[i - 1][j],  # Delete from word1
                        dp[i][j - 1],  # Insert into word1
                        dp[i - 1][j - 1],  # Replace in word1
                    )

        return dp[m][n]
