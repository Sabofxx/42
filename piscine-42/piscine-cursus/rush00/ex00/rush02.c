/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   rush02.c                                           :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: omischle <marvin@42.fr>                    +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2025/11/29 11:31:16 by omischle          #+#    #+#             */
/*   Updated: 2025/11/29 13:11:10 by omischle         ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

void	ft_putchar(char c);

void	go_colonne_print(int x, int compte_col, char *toolbox)
{
	if (compte_col == 1)
		ft_putchar(toolbox [0]);
	else if (compte_col == x)
		ft_putchar(toolbox [2]);
	else
		ft_putchar(toolbox [1]);

}

void	go_ligne(int x,int y,int compte_col,int compte_ligne)
{
	char toolbox [3];
	if (compte_ligne == 1)
	{
		toolbox [0] = 'A';
		toolbox [1] = 'B';
		toolbox [2] = 'A';
	}
	else if (compte_ligne == y)
	{
		toolbox [0] = 'C';
		toolbox [1] = 'B';
		toolbox [2] = 'C';
	}
	else
	{
		toolbox [0] = 'B';
		toolbox [1] = ' ';
		toolbox [2] = 'B';
	}
	go_colonne_print(x,compte_col, toolbox);
}

void rush( int x, int y)
{
	int compte_ligne;
	int compte_col;
		
	if (y < 1 || x < 1)
	{
		return ;
	}

	compte_ligne = 1;
	while ( compte_ligne <= y)
	{
		compte_col = 1;
		while (compte_col <= x)
		{
			go_ligne(x,y,compte_col,compte_ligne);
			compte_col++;
		}
		ft_putchar('\n');
		compte_ligne++;
	}
}
