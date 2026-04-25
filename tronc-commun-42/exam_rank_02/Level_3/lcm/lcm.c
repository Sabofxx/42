/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   lcm.c                                              :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: alex <alex@student.42.fr>                  +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2024/04/17 13:26:04 by alex              #+#    #+#             */
/*   Updated: 2024/04/17 17:13:50 by alex             ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

unsigned int	lcm(unsigned int a, unsigned int b)
{
	unsigned int	div;

	if (a == 0 || b == 0)
		return (0);
	div = 2;
	while (1)
	{
		if (a % div == 0 && b % div == 0)
			return (div);
		else if (div > a || div > b)
			return (1);
		div++;
	}
}

/* int	main(void)
{
	("%d\n", lcm(42, 15));
	return (0);
} */
